#! /usr/bin/env python
# -*- encoding: utf-8 -*-

"""
A typing game that measures WPM (words per minute).
"""

import contextlib
import curses
import random
import time

__author__ = "Christian Stigen Larsen"
__copyright__ = "Copyright 2017 Christian Stigen Larsen"
__license__ = "GNU GPL v3 or later"

# TODO:
# - Word-wrapping
# - Use urwid for terminal handling instead of curses
# - Add author/title to texts
# - More texts. Read from somewhere? Fortune?
# - Keep a running average of progression
# - Handle CTRL+BACKSPACE, ALT+BACKSPACE that immediately sets incorrect=0
# - Probably good idea to show what erronous keypressed were made.
#   Fill up a buffer, whenever you hit space, this buffer is erased

texts = [
    "I took a deep breath and listened to the old brag of my heart. I am, I am, I am.",
    "The most beautiful things in the world cannot be seen or touched, they are felt with the heart.",
    "Why, sometimes I've believed as many as six impossible things before breakfast.",
    "We are all in the gutter, but some of us are looking at the stars.",
    "Sometimes I can hear my bones straining under the weight of all the lives I'm not living.",
    "But I tried, didn't I? Goddamnit, at least I did that.",
]

def is_backspace(key):
    return key == 127 or key == curses.KEY_BACKSPACE or key == curses.KEY_DC

def is_escape(key):
    # This really isn't a good way to catch the escape char, because it seems
    # that if you press e.g. DELETE, it will send an escape sequence. Meaning
    # that the application will exit.
    return key == 27

@contextlib.contextmanager
def curses_screen():
    screen = curses.initscr()

    curses.noecho()
    curses.cbreak()
    screen.keypad(True)

    try:
        yield screen
    finally:
        curses.nocbreak()
        screen.keypad(False)
        curses.echo()
        curses.endwin()

class GameRound(object):
    def __init__(self, window, text):
        self.window = window
        self.text = text
        self.start = None
        self.position = 0
        self.incorrect = 0
        self.total_incorrect = 0
        self.edit_buffer = ""

    def run(self):
        while True:
            self.show_stats()
            self.show_edit_buffer()
            self.show_text()
            self.window.refresh()

            if self.finished:
                self.show_edit_buffer(clear=True)
                break

            key = self.get_key()
            if key is not None:
                self.handle_key(key)

    @property
    def elapsed(self):
        """Elapsed round time."""
        if self.start is None:
            return 0
        return time.time() - self.start

    @property
    def wpm(self):
        """Words per minute."""
        if self.start is None:
            return 0
        return (60.0 * self.position / 5.0) / self.elapsed

    @property
    def cps(self):
        """Characters per second."""
        if self.start is None:
            return 0
        return float(self.position) / self.elapsed

    @property
    def cursor(self):
        """Cursor position within text."""
        return self.position + self.incorrect

    @property
    def accuracy(self):
        n = len(self.text)
        i = self.total_incorrect
        return float(n) / (n+i)

    def show_stats(self):
        self.window.addstr(0, 0, " "*(curses.COLS-1))
        self.window.addstr(0, 0, "%5.1f WPM   %4.1f CPS   %.1fs   %.1f%% acc" % (self.wpm,
            self.cps, self.elapsed, 100.0*self.accuracy))

    def show_text(self):
        self.window.addstr(2, 0, self.text[:self.position], curses.A_BOLD)
        self.window.addstr(2, self.position, self.text[self.position:])

        if self.incorrect > 0:
            self.window.addstr(2, self.position,
                    self.text[self.position:self.cursor], curses.color_pair(1))

        # Back to current position in text
        self.window.move(2, self.cursor)

    def show_edit_buffer(self, clear=False):
        self.window.addstr(4, 0, " "*(curses.COLS-1))
        if not clear:
            self.window.addstr(4, 0, self.edit_buffer)

    def get_key(self):
        try:
            return self.window.getkey()
        except KeyboardInterrupt:
            raise
        except:
            return None

    @property
    def finished(self):
        return self.incorrect == 0 and (self.position == len(self.text))

    def handle_key(self, key):
        if is_escape(ord(key)):
            raise KeyboardInterrupt()

        if is_backspace(ord(key)):
            if self.incorrect > 0:
                self.incorrect -= 1
                self.edit_buffer = self.edit_buffer[:-1]
            return

        # Start recording upon first ordinary key press
        if self.start is None:
            self.start = time.time()

        # Correct key at correct location?
        self.edit_buffer += key
        if self.incorrect == 0 and key == self.text[self.position]:
            self.position += 1
            if key == " ":
                self.edit_buffer = ""
        else:
            self.incorrect += 1
            self.total_incorrect += 1

def main():
    with curses_screen():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)

        window = curses.newwin(curses.LINES, curses.COLS, 0, 0)

        while True:
            window.clear()
            window.timeout(20)

            game = GameRound(window, random.choice(texts))
            game.run()

            window.addstr(4, 0, "Press any key to continue or ESC to quit")

            window.timeout(-1)
            if window.getch() == 27:
                raise KeyboardInterrupt()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
