# -*- encoding: utf-8 -*-

"""
Measures your typing speed in words per minute (WPM).

This file is part of the wpm software.
Copyright 2017, 2018 Christian Stigen Larsen

Distributed under the GNU Affero General Public License (AGPL) v3 or later. See
the file LICENSE.txt for the full license text. This software makes use of open
source software.

The quotes database is *not* covered by the AGPL!
"""

import curses
import time

from wpm.config import Config
from wpm.error import WpmError
from wpm.record import Recorder
from wpm.screen import Screen

class GameManager(object):
    """The main game runner."""
    def __init__(self, quotes, stats, cpm_flag, monochrome):
        self.config = Config()
        self.stats = stats
        self.cpm_flag = cpm_flag
        self.average = self.stats.average(self.stats.tag, last_n=10)
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

        self.screen = Screen(monochrome)
        self.set_quote(self.quotes.next())

    def __enter__(self):
        return self

    def __exit__(self, error_type, error_value, error_traceback):
        self.screen.deinit()
        if error_type is not None:
            return False
        return self

    def set_tab_spaces(self, spaces):
        """Sets how many spaces a tab should expand to."""
        self.tab_spaces = spaces

    def mark_finished(self):
        """Marks current race as finished."""
        self.stop = time.time()
        self.stats.add(self.wpm(self.elapsed),
                       self.accuracy,
                       self.quote.text_id,
                       self.quotes.database)

        self.average = self.stats.average(self.stats.tag, last_n=10)

    def set_quote(self, quote):
        """Sets current quote."""
        self.quote = quote
        self.recorder = Recorder()
        self.screen.set_quote(self.quote)

    @property
    def is_typing(self):
        """Is user currently typing a quote?"""
        return (self.start is not None) and (self.stop is None)

    @property
    def game_done(self):
        """Has user finished a quote?"""
        return (self.start is not None) and (self.stop is not None)

    def run(self, to_front=None):
        """Starts the main game loop."""
        self.set_tab_spaces(self.config.wpm.tab_spaces)

        if to_front:
            self.quotes.put_to_front(to_front)
            self.set_quote(self.quotes.current())

        key = None
        while True:
            self.now = time.time()

            head = self.get_stats(self.elapsed)

            if self.is_typing:
                if self.screen.first_key:
                    self.screen.first_key = False
                    self.recorder.reset()
                    self.screen.rerender_race(head)

                self.screen.show_keystroke(head,
                                           self.position,
                                           self.incorrect,
                                           self._edit,
                                           key)
            elif self.game_done:
                self.screen.show_score(head,
                                       self.wpm(self.elapsed),
                                       self.stats,
                                       self.cpm_flag)
            else:
                self.screen.show_browser(head, self.stats, self.cpm_flag)

            self.screen.window.refresh()
            key = self.screen.get_key()
            self.handle_key(key)

    def wpm(self, elapsed):
        """Words per minute."""
        if self.start is None:
            return 0
        return min((60.0 * self.position / 5.0) / elapsed, 999)

    def cps(self, elapsed):
        """Characters per second."""
        if self.start is None:
            return 0
        return min(float(self.position) / elapsed, 99)

    @property
    def elapsed(self):
        """Elapsed game round time."""
        if self.start is None:
            # Typing has not started
            return 0
        if self.stop is None:
            # Currently typing
            return self.now - self.start
        # Done typing
        return self.stop - self.start

    @property
    def accuracy(self):
        """Returns typing accuracy."""
        if self.start is None:
            return 0

        length = len(self.quote.text)
        return float(length) / (length + self.total_incorrect)

    def get_stats(self, elapsed):
        """Returns the top-bar stats line."""
        kbd = self.stats.tag

        parts = (
            "%5.1f wpm" % self.wpm(elapsed),
            " %4.1f cps" % self.cps(elapsed),
            " %5.2fs" % elapsed,
            " %5.1f%% acc" % (100.0*self.accuracy),
            " %5.1f avg wpm" % self.average,
            " - " + (kbd if kbd is not None else "Unspecified"),
        )

        stat = ""

        for part in parts:
            if (len(stat) + len(part)) <= self.screen.columns:
                stat += part

        return stat

    def reset(self, direction=0):
        """Cancels current game."""
        self.start = None
        self.stop = None

        self.position = 0
        self.incorrect = 0
        self.total_incorrect = 0
        self.cheight = 0

        self._edit = ""
        self.screen.first_key = True
        self.screen.clear_prompt()

        if direction:
            if direction > 0:
                self.set_quote(self.quotes.next())
            else:
                self.set_quote(self.quotes.previous())
            self.screen.clear()

    def resize(self):
        """Handles a resized terminal."""
        max_y, max_x = self.screen.window.getmaxyx()
        self.screen.clear()

        # Check if we have the resizeterm ncurses extension
        if hasattr(curses, "resizeterm"):
            curses.resizeterm(max_y, max_x)
            # An ungetch for KEY_RESIZE will be sent to let others handle it.
            # We'll just pop it off again to prevent endless loops.
            self.screen.get_key()

        self.screen.set_quote(self.quote)

        if self.start is not None and self.stop is None:
            # Resize during typing requires redrawing quote.
            self.screen.update_quote(Screen.COLOR_QUOTE)
            self.screen.update_author()

            if self.position + self.incorrect <= len(self.quote.text):
                for pos in range(self.position + 1):
                    self.screen.highlight_progress(pos, 0)
                for inc in range(self.incorrect + 1):
                    self.screen.highlight_progress(self.position, inc)

    def handle_key(self, key):
        """Dispatches actions based on key and current mode."""
        # TODO: Refactor this mess of a function
        if key is None:
            return

        if key == "KEY_RESIZE":
            self.resize()
            return

        # Browse mode
        if self.start is None or (self.start is not None and
                                  self.stop is not None):
            if key in (" ", "KEY_LEFT", "KEY_RIGHT"):
                self.reset(direction=-1 if key == "KEY_LEFT" else 1)
                return
            elif Screen.is_escape(key):
                # Exit program
                raise KeyboardInterrupt()

        if Screen.is_escape(key):
            self.reset()
            return

        self.recorder.add(self.elapsed, key, self.position, self.incorrect)

        if Screen.is_backspace(key):
            if self.incorrect:
                self.incorrect -= 1
                self._edit = self._edit[:-1]
            elif self._edit:
                self.position -= 1
                self._edit = self._edit[:-1]
            return

        if self.stop is not None:
            # Use wants to try again immediately after score
            self.reset()
            head = self.get_stats(self.elapsed)
            self.screen.rerender_race(head)
            self.screen.show_keystroke(head,
                                       self.position,
                                       self.incorrect,
                                       self._edit,
                                       key)

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
                self.screen.clear_prompt()
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
