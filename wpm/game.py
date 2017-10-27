#! /usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Measures your typing speed in words per minute (WPM).

This file is part of the wpm software.
Copyright 2017 Christian Stigen Larsen

Distributed under the GNU GPL v3 or later. See the file LICENSE.txt for the
full license text. This software makes use of open source software.
"""

import codecs
import contextlib
import curses
import curses.ascii
import json
import os
import time

class Screen(object):
    def __init__(self):
        # Make delay slower
        os.environ.setdefault("ESCDELAY", "25")

        self.screen = curses.initscr()
        self.screen.keypad(True)

        curses.noecho()
        curses.cbreak()

        curses.start_color()

        if os.getenv("TERM") == "xterm-256color":
            # Incorrect
            curses.init_pair(1, 197, 52)

            # Status
            curses.init_pair(2, 51, 24)

            # Done text
            curses.init_pair(3, 240, 0)

            # Normal text
            curses.init_pair(4, 230, 0)

            # Edit text
            curses.init_pair(5, 244, 0)
        else:
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
            curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)

        self.window = curses.newwin(curses.LINES, curses.COLS, 0, 0)
        self.window.keypad(True)
        self.window.timeout(20)

    def is_escape(self, key):
        return ord(key) == curses.ascii.ESC

    def is_backspace(self, key):
        if len(key) > 1:
            return key == "KEY_BACKSPACE"
        elif ord(key) in (curses.ascii.BS, curses.ascii.DEL):
            return True
        return False

    def getkey(self):
        try:
            return self.window.getkey()
        except KeyboardInterrupt:
            raise
        except:
            return None

    def update(self, browse, head, quote, position, incorrect, author, title,
            typed):
        cursor = 0
        cols = curses.COLS
        quote = quote.encode("utf-8")

        # Show header
        self.window.addstr(0, 0, head + " "*(curses.COLS - len(head)),
                curses.color_pair(2))

        if browse:
            self.window.addstr(2, 0, quote, curses.color_pair(4 if browse==1
                else 3))

            # Show author
            credit = u"    - %s, %s" % (author, title)
            self.window.addstr(4 + (len(quote) // cols), 0,
                    credit.encode("utf-8"), curses.color_pair(5))
            typed = "Use arrows or space to browse quotes, esc to quit, or start typing"
        elif position < len(quote):
            cursor = position + incorrect
            color = curses.color_pair(3 if incorrect == 0 else 1)

            self.window.chgat(2 + ((cursor - 1) // cols), ((cursor - 1) %
                cols), 1, color)
            self.window.chgat(2 + ((cursor + 1) // cols), ((cursor + 1) %
                cols), 1, curses.color_pair(4))

            typed = "> " + typed

        # Show typed text
        self.window.addstr(10, 0, typed, curses.color_pair(5))
        self.window.clrtoeol()

        # Move cursor to current position in text before refreshing
        if browse <= 1:
            self.window.move(2 + (cursor // cols), cursor % cols)
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
        self.quotes = quotes.random_iterator()
        self.quote = self.quotes.next()
        self.text = self.quote["text"]

        self.screen = Screen()

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.screen.deinit()
        if type is not None:
            return False
        else:
            return self

    def set_tab_spaces(self, spaces):
        self.tab_spaces = spaces

    def mark_finished(self):
        self.stop = time.time()
        self.stats.add(self.wpm(self.elapsed), self.accuracy)
        self.average = self.stats.average(self.stats.keyboard, last_n=10)

    def run(self):
        while True:
            is_typing = self.start is not None and self.stop is None

            browse = int(not is_typing)
            if self.stop is not None:
                browse = 2

            self.screen.update(browse, self.get_stats(self.elapsed),
                    self.text, self.position, self.incorrect,
                    self.quote["author"], self.quote["title"], self._edit)

            key = self.screen.getkey()
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
            n = len(self.text)
            return float(n) / (n + self.total_incorrect)

    def get_stats(self, elapsed):
        keyboard = self.stats.keyboard
        if keyboard is None:
            keyboard = "Unspecified"

        return "%5.1f wpm   %4.1f cps   %5.2fs   %5.1f%% acc   %5.1f avg wpm   kbd: %s" % (
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
            self.text = self.quote["text"]
            self.screen.clear()

    def handle_key(self, key):
        if key == curses.KEY_RESIZE:
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
                    self.text, self.position, self.incorrect,
                    self.quote["author"], self.quote["title"], self._edit)

        # Start recording upon first ordinary key press
        if self.start is None:
            self.start = time.time()

        if key == curses.KEY_ENTER:
            key = "\n"
        elif key == "\t" and self.tab_spaces is not None:
            key = " "*self.tab_spaces

        self._edit += key

        # Did the user strike the correct key?
        if self.incorrect == 0 and self.text[self.position] == key:
            self.position += 1

            # Reset edit buffer on a correctly finished word
            if key == " " or key == "\n":
                self._edit = ""

            # Finished typing?
            if self.position == len(self.text):
                self.mark_finished()
        else:
            self.incorrect += 1
            self.total_incorrect += 1
