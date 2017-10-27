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
import json
import os
import time

def is_escape(key):
    # TODO: Escape detection doesn't work very well with curses right now
    return key == 27 or key == ""

def is_backspace(key):
    return key in (127, curses.KEY_BACKSPACE, curses.KEY_DC, "")

class Screen(object):
    def __init__(self):
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
        self.window.timeout(20)

    def getkey(self):
        try:
            return self.window.getkey()
        except KeyboardInterrupt:
            raise
        except:
            return None

    def update(self, browse, head, quote, position, incorrect, author, title,
            typed):
        # TODO: While typing, only need to update previous character, for
        # speed.

        # Show header
        self.window.addstr(0, 0, head, curses.color_pair(2))
        self.window.clrtoeol()

        if browse:
            self.window.addstr(2, 0, quote, curses.color_pair(4))
            cursor = 0
        elif position < len(quote):
            cursor = position + incorrect
            color = curses.color_pair(3 if incorrect == 0 else 1)
            self.window.chgat(2 + (cursor // curses.COLS), ((cursor - 1) %
                    curses.COLS), 1, color)
            if incorrect > 0:
                self.window.chgat(2 + ((cursor+1) // curses.COLS), (cursor %
                    curses.COLS), 1, curses.color_pair(4))

            # Done text
            #self.window.addstr(2, 0, quote[:position], curses.color_pair(3))

            # Rest of text
            #self.window.addstr(2, position, quote[position:], curses.color_pair(4))

            #if incorrect > 0:
                #self.window.addstr(2, position, quote[position:cursor],
                        #curses.color_pair(1))
        else:
            cursor = 0

        # Show author
        credit = "    - %s, %s" % (author, title)
        # TODO: Doesn't handle unicode!
        self.window.addstr(4 + (len(quote) // curses.COLS), 0, credit,
                curses.color_pair(4))

        # Show typed text
        if browse:
            typed = ""
        else:
            typed = "> " + typed
        self.window.addstr(10, 0, typed, curses.color_pair(5))
        self.window.clrtoeol()

        # Move cursor to current position in text before refreshing
        self.window.move(2 + (cursor // curses.COLS), cursor % curses.COLS)
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
        self.quotes = quotes.random_iterator()
        self.quote = self.quotes.next()
        self.text = self.quote["text"].strip().replace("  ", " ")
        self.start = None
        self.position = 0
        self.incorrect = 0
        self.total_incorrect = 0
        self._edit = ""
        self.average = self.stats.average(self.stats.keyboard, last_n=10)
        self.tab_spaces = None
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
        if self.finished and self.start is not None:
            elapsed = self.elapsed
            self.stats.add(self.wpm(elapsed), self.accuracy)
            self.average = self.stats.average(self.stats.keyboard, last_n=10)

    def run(self):
        while True:
            self.screen.update(not self.typing, self.get_stats(self.elapsed),
                    self.text, self.position, self.incorrect,
                    self.quote["author"], self.quote["title"], self._edit)
            key = self.screen.getkey()
            if key is not None:
                self.handle_key(key)

    @property
    def elapsed(self):
        """Elapsed game round time."""
        if self.start is None:
            return 0
        else:
            return time.time() - self.start

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
    def accuracy(self):
        if self.start is None:
            return 0
        else:
            n = len(self.text)
            return float(n) / (n + self.total_incorrect)

    def get_stats(self, elapsed):
        return "%5.1f wpm   %4.1f cps   %5.2fs   %5.1f%% acc   %5.1f avg wpm   kbd: %s" % (
                self.wpm(elapsed), self.cps(elapsed), elapsed,
                100.0*self.accuracy, self.average, "Unspecified" if self.stats.keyboard is
                None else self.stats.keyboard)

    @property
    def finished(self):
        return self.incorrect == 0 and (self.position == len(self.text))

    def reset(self, direction=0):
        self.start = None
        self.position = 0
        self.incorrect = 0
        self.total_incorrect = 0
        self._edit = ""
        if direction:
            if direction > 0:
                self.quote = self.quotes.next()
            else:
                self.quote = self.quotes.previous()
            self.text = self.quote["text"].strip().replace("  ", " ")
            self.screen.clear()

    @property
    def typing(self):
        return not (self.finished or self.start is None)

    def handle_key(self, key):
        if is_escape(key):
            if self.start is not None:
                # Escape during typing gets you back to the "menu"
                self.reset()
                return
            else:
                raise KeyboardInterrupt()

        # Browse
        if not self.typing and key in (" ", curses.KEY_LEFT, curses.KEY_RIGHT):
            self.reset(direction=-1 if key == curses.KEY_LEFT else 1)
            return

        if is_backspace(key):
            if self.incorrect > 0:
                self.incorrect -= 1
            elif len(self._edit) > 0:
                self.position -= 1
            self._edit = self._edit[:-1]
            return

        # Start recording upon first ordinary key press
        if self.start is None:
            self.start = time.time()

        # Correct key at correct location?
        if len(key) == 1:
            self._edit += key

        if key == curses.KEY_ENTER:
            key = "\n"
        elif key == "\t" and self.tab_spaces is not None:
            key = " "*self.tab_spaces
        elif len(key) > 1:
            return

        if (self.incorrect == 0 and
                self.text[self.position:self.position+len(key)] == key):
            self.position += len(key)
            if key.startswith(" ") or key == "\n":
                self._edit = ""
            if self.finished:
                self.mark_finished()
        else:
            self.incorrect += 1
            self.total_incorrect += 1
