#! /usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Measures your typing speed in words per minute (WPM).

This file is part of the wpm software.
Copyright 2017 Christian Stigen Larsen

Distributed under the GNU GPL v3 or later. See the file LICENSE.txt for the
full license text. This software makes use of open source software.
"""

import curses
import curses.ascii
import locale
import os
import sys
import time
import wpm.config
import wpm.error

def word_wrap(s, w):
    """Returns lengths of lines that can be printed without wrapping."""
    lengths = []
    while len(s) > w:
        end = s[:w+1].rindex(" ")

        # We can't divide the input nicely, so just display it as-is
        if end == -1:
            return [len(s)]

        lengths.append(end)
        s = s[end+1:]

    if len(s) > 0:
        lengths.append(len(s))

    return lengths

def screen_coords(lens, pos):
    for y, l in enumerate(lens):
        if pos <= l:
            break
        pos -= (l+1)
    return pos, y

class Screen(object):
    def __init__(self):
        self.config = wpm.config.Config()

        # Make delay slower
        os.environ.setdefault("ESCDELAY", self.config.escdelay)

        # I can't remember why we set LC_ALL to an empty string. Figure it out,
        # cause it doesn't look too smart.
        locale.setlocale(locale.LC_ALL, "")

        self.screen = curses.initscr()
        self.screen.nodelay(True)

        if curses.LINES < 12:
            curses.endwin()
            raise wpm.error.WpmError(
                    "wpm requires at least 12 lines in your display")

        if curses.COLS < 51:
            curses.endwin()
            raise wpm.error.WpmError(
                    "wpm requires at least 51 columns in your display")

        self.screen.keypad(True)
        curses.noecho()
        curses.cbreak()
        curses.start_color()

        if os.getenv("TERM").endswith("256color"):
            bg = self.config.background_color_256

            # Incorrect
            curses.init_pair(1, *self.config.incorrect_color_256)

            # Status
            curses.init_pair(2, *self.config.status_color_256)

            # Done text
            curses.init_pair(3, *self.config.correct_color_256)

            # Normal text
            curses.init_pair(4, *self.config.quote_color_256)

            # UNUSED
            curses.init_pair(5, 244, bg)

            # Author
            curses.init_pair(6, *self.config.author_color_256)

            # Edit text and info
            curses.init_pair(7, *self.config.prompt_color_256)

            # Background color
            curses.init_pair(8, bg, bg)

            # Score highlight
            curses.init_pair(9, *self.config.score_highlight_color_256)

        else:
            bg = self.config.background_color

            # Incorrect
            curses.init_pair(1, *self.config.incorrect_color)

            # Status
            curses.init_pair(2, *self.config.status_color)

            # Done text
            curses.init_pair(3, *self.config.correct_color)

            # Normal text
            curses.init_pair(4, *self.config.quote_color)

            # UNUSED
            curses.init_pair(5, curses.COLOR_WHITE, bg)

            # Author
            curses.init_pair(6, *self.config.author_color)

            # Edit text and info
            curses.init_pair(7, *self.config.prompt_color)

            # Background color
            curses.init_pair(8, bg, bg)

            # Score highlight
            curses.init_pair(9, *self.config.score_highlight_color)

        self.window = curses.newwin(curses.LINES, curses.COLS, 0, 0)
        self.window.keypad(True)
        self.window.timeout(self.config.window_timeout)
        self.window.bkgd(" ", curses.color_pair(8))

    def is_escape(self, key):
        if len(key) == 1:
            return ord(key) == curses.ascii.ESC
        return False

    def is_backspace(self, key):
        if len(key) > 1:
            return key == "KEY_BACKSPACE"
        elif ord(key) in (curses.ascii.BS, curses.ascii.DEL):
            return True
        return False

    def get_key(self):
        # Install a suitable get_key based on Python version
        if sys.version_info[0:2] >= (3, 3):
            self.get_key = self.getkey_py33
        else:
            self.get_key = self.getkey_py27
        return self.get_key()

    def getkey_py33(self):
        try:
            # Curses in Python 3.3 handles unicode via get_wch
            key = self.window.get_wch()
            if type(key) == int:
                if key == curses.KEY_LEFT:
                    return "KEY_LEFT"
                elif key == curses.KEY_RIGHT:
                    return "KEY_RIGHT"
                elif key == curses.KEY_RESIZE:
                    return "KEY_RESIZE"
                else:
                    return None
            return key
        except curses.error:
            return None
        except KeyboardInterrupt:
            raise

    def getkey_py27(self):
        try:
            return self.window.getkey()
        except KeyboardInterrupt:
            raise
        except curses.error:
            return None

    def column(self, y, x, width, text, attr=None, left=True):
        lengths = word_wrap(text, width)
        for y, length in enumerate(lengths, y):
            if left:
                self.window.addstr(y, x, text[:length].encode("utf-8"), attr)
            else:
                self.window.addstr(y, x - length, text[:length].encode("utf-8"), attr)
            text = text[1+length:]
        return len(lengths)

    def update(self, browse, head, quote, position, incorrect, author, title,
            typed, wpm, average):
        cols = curses.COLS
        lengths = word_wrap(quote, cols - 1)
        sx, sy = screen_coords(lengths, position)
        h = len(lengths)

        # Show header
        self.window.addstr(0, 0, head + " "*(cols - len(head)),
                curses.color_pair(2))

        if browse:
            # Display quote
            color = curses.color_pair(4 if browse == 1 else 3)
            for y, length in enumerate(lengths, 2):
                self.window.addstr(y, 0, quote[:length], color)
                quote = quote[1+length:]

            # Show author
            credit = u"— %s, %s" % (author, title)
            self.cheight = 4 + h + self.column(3+h, cols - 10, cols//2, credit,
                    curses.color_pair(6), False)
            if browse >= 2:
                typed = "You scored %.1f wpm%s " % (wpm, "!" if wpm > average
                        else ".")
            else:
                typed = ""
            typed += "Use arrows/space to browse, esc to quit, or start typing."
        elif position < len(quote):
            color = curses.color_pair(3 if incorrect == 0 else 1)
            typed = "> " + typed

            if position + incorrect < len(quote):
                sx, sy = screen_coords(lengths, position + incorrect - 1)
                self.window.chgat(2 + sy, max(sx, 0), 1, color)

                sx, sy = screen_coords(lengths, position + incorrect + 1)
                self.window.chgat(2 + sy, sx, curses.color_pair(4))

        # Show typed text
        if self.cheight < curses.LINES:
            self.window.move(self.cheight, 0)
            self.window.clrtoeol()
            self.window.addstr(self.cheight, 0, typed, curses.color_pair(7))
        if browse > 1:
            # If done, highlight score
            self.window.chgat(self.cheight, 11,
                len(str("%.1f" % wpm)), curses.color_pair(9))

        # Move cursor to current position in text before refreshing
        if browse < 1:
            sx, sy = screen_coords(lengths, position + incorrect)
            self.window.move(2 + sy, min(sx, cols - 1))
        else:
            self.window.move(2, 0)

        self.window.refresh()

    def clear(self):
        self.window.clear()

    def deinit(self):
        curses.nocbreak()
        self.screen.keypad(False)
        curses.echo()
        curses.endwin()

class Game(object):
    def __init__(self, quotes, stats):
        self.config = wpm.config.Config()
        self.stats = stats
        self.average = self.stats.average(self.stats.keyboard, last_n=10)
        self.tab_spaces = None

        # Stats
        self.position = 0
        self.incorrect = 0
        self.total_incorrect = 0

        self.start = None
        self.stop = None

        self._edit = ""
        self.num_quotes = len(quotes)
        self.quotes = quotes.random_iterator()
        self.quote = self.quotes.next()

        self.screen = Screen()

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.screen.deinit()
        if type is not None:
            return False
        else:
            return self

    def jump_to(self, text_id):
        """Skips until then given text id is found."""
        pos = 0
        while self.quote.text_id != text_id:
            self.quote = self.quotes.next()
            pos += 1
            if pos > self.num_quotes:
                raise KeyError("Text ID not found: %s" % text_id)

    def set_tab_spaces(self, spaces):
        self.tab_spaces = spaces

    def mark_finished(self):
        self.stop = time.time()
        self.stats.add(self.wpm(self.elapsed), self.accuracy,
                self.quote.text_id, self.quotes.database)
        self.average = self.stats.average(self.stats.keyboard, last_n=10)

    def run(self):
        while True:
            is_typing = self.start is not None and self.stop is None

            browse = int(not is_typing)
            if self.stop is not None:
                browse = 2

            self.screen.update(browse, self.get_stats(self.elapsed),
                    self.quote.text, self.position, self.incorrect,
                    self.quote.author, self.quote.title, self._edit,
                    self.wpm(self.elapsed), self.average)

            key = self.screen.get_key()
            if key is not None:
                self.handle_key(key)

    def wpm(self, elapsed):
        """Words per minute."""
        if self.start is None:
            return 0
        else:
            return min((60.0 * self.position / 5.0) / elapsed, 999)

    def cps(self, elapsed):
        """Characters per second."""
        if self.start is None:
            return 0
        else:
            return min(float(self.position) / elapsed, 99)

    @property
    def elapsed(self):
        """Elapsed game round time."""
        if self.start is None:
            # Typing has not started
            return 0
        elif self.stop is None:
            # Currently typing
            return time.time() - self.start
        else:
            # Done typing
            return self.stop - self.start

    @property
    def accuracy(self):
        if self.start is None:
            return 0
        else:
            n = len(self.quote.text)
            return float(n) / (n + self.total_incorrect)

    def get_stats(self, elapsed):
        keyboard = self.stats.keyboard
        if keyboard is None:
            keyboard = "Unspecified"

        return "%5.1f wpm %4.1f cps %5.2fs %5.1f%% acc %5.1f avg wpm - %s" % (
                self.wpm(elapsed),
                self.cps(elapsed),
                elapsed,
                100.0*self.accuracy,
                self.average,
                keyboard)

    def reset(self, direction=0):
        self.start = None
        self.stop = None

        self.position = 0
        self.incorrect = 0
        self.total_incorrect = 0

        self._edit = ""

        if direction:
            if direction > 0:
                self.quote = self.quotes.next()
            else:
                self.quote = self.quotes.previous()
            self.screen.clear()

    def resize(self):
        y, x = self.screen.window.getmaxyx()
        self.screen.clear()
        curses.resizeterm(y, x)

    def handle_key(self, key):
        if key == "KEY_RESIZE":
            self.resize()
            return

        # Browse mode
        if self.start is None or (self.start is not None and self.stop is not
                None):
            if key in (" ", "KEY_LEFT", "KEY_RIGHT"):
                self.reset(direction=-1 if key == "KEY_LEFT" else 1)
                return
            elif self.screen.is_escape(key):
                # Exit program
                raise KeyboardInterrupt()

        if self.screen.is_escape(key):
            self.reset()
            return

        if self.screen.is_backspace(key):
            if self.incorrect > 0:
                self.incorrect -= 1
                self._edit = self._edit[:-1]
            elif len(self._edit) > 0:
                self.position -= 1
                self._edit = self._edit[:-1]
            return

        # Try again?
        if self.stop is not None:
            self.reset()
            self.screen.clear()
            self.screen.update(1, self.get_stats(self.elapsed),
                    self.quote.text, self.position, self.incorrect,
                    self.quote.author, self.quote.title, self._edit,
                    self.wpm(self.elapsed), self.average)

        # Start recording upon first ordinary key press
        if self.start is None:
            self.start = time.time()

        if key == curses.KEY_ENTER:
            key = "\n"
        elif key == "\t" and self.tab_spaces is not None:
            key = " "*self.tab_spaces

        # Did the user strike the correct key?
        if self.incorrect == 0 and self.quote.text[self.position] == key:
            self.position += 1

            # Reset edit buffer on a correctly finished word
            if key == " " or key == "\n":
                self._edit = ""
            else:
                self._edit += key

            # Finished typing?
            if self.position == len(self.quote.text):
                self.mark_finished()
        elif self.incorrect + self.position < len(self.quote.text):
            self.incorrect += 1
            self.total_incorrect += 1
            if key == "\n":
                key = " "
            self._edit += key
