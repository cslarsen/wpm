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
import curses.ascii
import locale
import os
import sys
import time
import wpm.config
import wpm.error

def word_wrap(text, width):
    """Returns lengths of lines that can be printed without wrapping."""
    lengths = []
    while len(text) > width:
        try:
            end = text[:width + 1].rindex(" ")
        except ValueError:
            break

        # We can't divide the input nicely, so just display it as-is
        if end == -1:
            return [len(text)]

        lengths.append(end)
        text = text[end + 1:]

    if text:
        lengths.append(len(text))

    return lengths

def screen_coords(lengths, position):
    """Translates quote offset into screen coordinates.

    Args:
        lengths: List of line lengths for the word-wrapped quote.
        position: Offset into the quote that we want to translate to screen
                  coordinates.

    Returns:
        Tuple containing X and Y screen coordinates.
    """
    y_position = 0

    for y_position, line_length in enumerate(lengths):
        if position <= line_length:
            break
        position -= line_length + 1

    return position, y_position

def pad_right(text, width):
    """Pads string with spaces on the right."""
    if len(text) < width:
        return text + " "*(width - len(text))
    return text


class Screen(object):
    """Renders the terminal screen."""

    COLOR_AUTHOR = 1
    COLOR_BACKGROUND = 2
    COLOR_CORRECT = 3
    COLOR_HISCORE = 4
    COLOR_INCORRECT = 5
    COLOR_PROMPT = 6
    COLOR_QUOTE = 7
    COLOR_STATUS = 8

    def __init__(self):
        self.config = wpm.config.Config()

        # Make delay slower
        os.environ.setdefault("ESCDELAY", self.config.escdelay)

        # Use the preferred system encoding
        locale.setlocale(locale.LC_ALL, "")
        self.encoding = locale.getpreferredencoding().lower()

        self.screen = curses.initscr()
        self.screen.nodelay(True)

        min_lines = 12
        if self.lines < min_lines:
            curses.endwin()
            raise wpm.error.WpmError(
                "wpm requires at least %d lines in your display" % min_lines)

        min_cols = 20
        if self.columns < min_cols:
            curses.endwin()
            raise wpm.error.WpmError(
                "wpm requires at least %d columns in your display" % min_cols)

        try:
            self.screen.keypad(True)
            curses.noecho()
            curses.cbreak()

            curses.start_color()
            self.set_colors()

            self.window = curses.newwin(self.lines, self.columns, 0, 0)
            self.window.keypad(True)
            self.window.timeout(self.config.window_timeout)
            self.window.bkgd(" ", Screen.COLOR_BACKGROUND)


            # Local variables related to quote. TODO: Move this mess to somewhere
            # else.
            self.cheight = 0
            self.quote = ""
            self.quote_author = ""
            self.quote_columns = 0
            self.quote_height = 0
            self.quote_lengths = tuple()
            self.quote_title = ""
            self.quote_coords = tuple()
        except:
            curses.endwin()
            raise

    @property
    def columns(self):
        """Returns number of terminal columns."""
        # pylint: disable=no-member
        return curses.COLS

    @property
    def lines(self):
        """Returns number of terminal lines."""
        # pylint: disable=no-member
        return curses.LINES

    def set_colors(self):
        """Sets up curses color pairs."""

        if os.getenv("TERM").endswith("256color"):
            bg_col = self.config.background_color_256
            curses.init_pair(Screen.COLOR_AUTHOR, *self.config.author_color_256)
            curses.init_pair(Screen.COLOR_BACKGROUND, bg_col, bg_col)
            curses.init_pair(Screen.COLOR_CORRECT, *self.config.correct_color_256)
            curses.init_pair(Screen.COLOR_HISCORE, *self.config.score_highlight_color_256)
            curses.init_pair(Screen.COLOR_INCORRECT, *self.config.incorrect_color_256)
            curses.init_pair(Screen.COLOR_PROMPT, *self.config.prompt_color_256)
            curses.init_pair(Screen.COLOR_QUOTE, *self.config.quote_color_256)
            curses.init_pair(Screen.COLOR_STATUS, *self.config.status_color_256)
        else:
            bg_col = self.config.background_color
            curses.init_pair(Screen.COLOR_AUTHOR, *self.config.author_color)
            curses.init_pair(Screen.COLOR_BACKGROUND, bg_col, bg_col)
            curses.init_pair(Screen.COLOR_CORRECT, *self.config.correct_color)
            curses.init_pair(Screen.COLOR_HISCORE, *self.config.score_highlight_color)
            curses.init_pair(Screen.COLOR_INCORRECT, *self.config.incorrect_color)
            curses.init_pair(Screen.COLOR_PROMPT, *self.config.prompt_color)
            curses.init_pair(Screen.COLOR_QUOTE, *self.config.quote_color)
            curses.init_pair(Screen.COLOR_STATUS, *self.config.status_color)

        # Rebind class variables
        Screen.COLOR_AUTHOR = curses.color_pair(Screen.COLOR_AUTHOR)
        Screen.COLOR_BACKGROUND = curses.color_pair(Screen.COLOR_BACKGROUND)
        Screen.COLOR_CORRECT = curses.color_pair(Screen.COLOR_CORRECT)
        Screen.COLOR_HISCORE = curses.color_pair(Screen.COLOR_HISCORE)
        Screen.COLOR_INCORRECT = curses.color_pair(Screen.COLOR_INCORRECT)
        Screen.COLOR_PROMPT = curses.color_pair(Screen.COLOR_PROMPT)
        Screen.COLOR_QUOTE = curses.color_pair(Screen.COLOR_QUOTE)
        Screen.COLOR_STATUS = curses.color_pair(Screen.COLOR_STATUS)

    @staticmethod
    def is_escape(key):
        """Checks for escape key."""
        if len(key) == 1:
            return ord(key) == curses.ascii.ESC
        return False

    @staticmethod
    def is_backspace(key):
        """Checks for backspace key."""
        if len(key) > 1:
            return key == "KEY_BACKSPACE"
        elif ord(key) in (curses.ascii.BS, curses.ascii.DEL):
            return True
        return False

    def get_key(self):
        """Gets a single key stroke."""
        # pylint: disable=method-hidden
        # Install a suitable get_key based on Python version
        if sys.version_info[0:2] >= (3, 3):
            self.get_key = self._get_key_py33
        else:
            self.get_key = self._get_key_py27
        return self.get_key()

    def _get_key_py33(self):
        """Python 3.3+ implementation of get_key."""
        # pylint: disable=too-many-return-statements
        try:
            # Curses in Python 3.3 handles unicode via get_wch
            key = self.window.get_wch()
            if isinstance(key, int):
                if key == curses.KEY_BACKSPACE:
                    return "KEY_BACKSPACE"
                elif key == curses.KEY_LEFT:
                    return "KEY_LEFT"
                elif key == curses.KEY_RIGHT:
                    return "KEY_RIGHT"
                elif key == curses.KEY_RESIZE:
                    return "KEY_RESIZE"
                return None
            return key
        except curses.error:
            return None
        except KeyboardInterrupt:
            raise

    def _get_key_py27(self):
        """Python 2.7 implementation of get_key."""
        # pylint: disable=too-many-return-statements
        try:
            key = self.window.getkey()

            # Start of UTF-8 multi-byte character?
            if self.encoding == "utf-8" and ord(key[0]) & 0x80:
                multibyte = key[0]
                cont_bytes = ord(key[0]) << 1
                while cont_bytes & 0x80:
                    cont_bytes <<= 1
                    multibyte += self.window.getkey()[0]
                return multibyte.decode(self.encoding)

            if isinstance(key, int):
                if key == curses.KEY_BACKSPACE:
                    return "KEY_BACKSPACE"
                elif key == curses.KEY_LEFT:
                    return "KEY_LEFT"
                elif key == curses.KEY_RIGHT:
                    return "KEY_RIGHT"
                elif key == curses.KEY_RESIZE:
                    return "KEY_RESIZE"
                return None
            return key.decode("ascii")
        except KeyboardInterrupt:
            raise
        except curses.error:
            return None

    def addstr(self, x_pos, y_pos, text, color=None):
        """Wraps call around curses.window.addsr."""
        if self.lines > y_pos >= 0:
            if x_pos >= 0 and (x_pos + len(text)) < self.columns:
                self.window.addstr(y_pos, x_pos, text, color)

    def set_cursor(self, x_pos, y_pos):
        """Sets cursor position."""
        if (y_pos < self.lines) and (x_pos < self.columns):
            self.window.move(y_pos, x_pos)

    def right_column(self, y_pos, x_pos, width, text):
        """Writes text to screen in coumns."""
        lengths = word_wrap(text, width)

        for cur_y, length in enumerate(lengths, y_pos):
            self.addstr(x_pos - length, cur_y,
                        text[:length].encode(self.encoding),
                        Screen.COLOR_AUTHOR)
            text = text[1+length:]

        return len(lengths)

    def update_quote(self, color):
        """Renders complete quote on screen."""
        quote = self.quote[:]
        for y_pos, length in enumerate(self.quote_lengths, 2):
            self.addstr(0, y_pos, quote[:length].encode(self.encoding), color)
            quote = quote[1 + length:]

    def update_author(self):
        """Renders author on screen."""
        author = u"— %s, %s" % (self.quote_author, self.quote_title)
        self.cheight = 4 + self.quote_height
        self.cheight += self.right_column(self.cheight - 1,
                                          self.quote_columns - 10,
                                          self.quote_columns // 2,
                                          author)

    def update_header(self, text):
        """Renders top-bar header."""
        # NOTE: If this doesn't show the full bar in the background color,
        # revert back to pad_right usage.
        self.addstr(0, 0, text, Screen.COLOR_STATUS)
        self.window.chgat(0, 0, self.columns, Screen.COLOR_STATUS)

    def setup_quote(self, quote):
        """Sets up variables used for a new quote."""
        # TODO: Move this stuff elsewhere
        if self.config.max_quote_width > 0:
            self.quote_columns = min(self.columns, self.config.max_quote_width)
        else:
            self.quote_columns = self.columns

        self.cheight = 0
        self.quote = quote.text
        self.quote_author = quote.author
        self.quote_title = quote.title
        self.quote_lengths = tuple(word_wrap(self.quote, self.quote_columns - 1))
        self.quote_height = len(self.quote_lengths)

        # Remember (x, y) position for each quote offset.
        self.quote_coords = []
        for offset in range(len(self.quote)+1):
            x_pos, y_pos = screen_coords(self.quote_lengths, offset)
            self.quote_coords.append((x_pos, y_pos))
        self.quote_coords = tuple(self.quote_coords)

    def update_prompt(self, prompt):
        """Prints prompt on the display."""
        self.set_cursor(0, self.cheight)
        self.window.clrtoeol()
        self.addstr(0, self.cheight, prompt.encode(self.encoding),
                    Screen.COLOR_PROMPT)

    def cursor_to_start(self):
        """Moves cursor to beginning of quote."""
        self.set_cursor(0, 2)

    def show_browser(self, head):
        """Show quote browsing screen."""
        self.update_header(head)
        self.update_quote(Screen.COLOR_QUOTE)
        self.update_author()
        self.update_prompt("Use arrows/space to browse, esc to quit, or start typing.")
        self.cursor_to_start()

    def show_score(self, head, wpm_score):
        """Show score screen after typing has finished."""
        self.update_header(head)
        self.update_quote(Screen.COLOR_CORRECT)
        self.update_author()

        self.update_prompt("You scored %.1f wpm. "
                           "Use arrows/space to browse, "
                           "esc to quit, or start typing." % wpm_score)

        # Highlight score
        self.window.chgat(self.cheight, 11, len(str("%.1f" % wpm_score)),
                          Screen.COLOR_HISCORE)

        self.cursor_to_start()

    def show_keystroke(self, head, position, incorrect, typed):
        """Updates the screen while typing."""
        self.update_header(head)

        if incorrect:
            color = Screen.COLOR_INCORRECT
        else:
            color = Screen.COLOR_CORRECT

        prompt = ""
        xpos, ypos = self.quote_coords[position + incorrect]

        if position + incorrect <= len(self.quote):
            # Highlight correct / incorrect character in quote
            ixpos, iypos = self.quote_coords[position + incorrect - 1]
            self.window.chgat(2 + iypos, max(ixpos, 0), 1, color)

            # Highlight next as correct, in case of backspace
            self.window.chgat(2 + ypos, xpos, 1, Screen.COLOR_QUOTE)
            prompt = "> " + typed

        # Show typed text
        if self.cheight < self.lines:
            self.update_prompt(prompt)

        # Move cursor to current position in text before refreshing
        self.set_cursor(min(xpos, self.quote_columns - 1), 2 + ypos)

    def clear(self):
        """Clears the screen."""
        self.window.clear()

    def deinit(self):
        """Deinitializes curses."""
        curses.nocbreak()
        self.screen.keypad(False)
        curses.echo()
        curses.endwin()


class Game(object):
    """The main game runner."""
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

        self.screen = Screen()
        self.quote = self.quotes.next()
        self.screen.setup_quote(self.quote)

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

        self.average = self.stats.average(self.stats.keyboard, last_n=10)

    def run(self, to_front=None):
        """Starts the main game loop."""
        if to_front:
            self.quotes.put_to_front(to_front)
            self.quote = self.quotes.current()
            self.screen.setup_quote(self.quote)

        while True:
            is_typing = self.start is not None and self.stop is None
            game_done = (not is_typing) and (self.stop is not None)

            if is_typing:
                self.screen.show_keystroke(self.get_stats(self.elapsed),
                                           self.position,
                                           self.incorrect,
                                           self._edit)
            elif game_done:
                self.screen.show_score(self.get_stats(self.elapsed),
                                       self.wpm(self.elapsed))
            else:
                self.screen.show_browser(self.get_stats(self.elapsed))

            key = self.screen.get_key()
            if key is not None:
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
        elif self.stop is None:
            # Currently typing
            return time.time() - self.start

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
        kbd = self.stats.keyboard

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

        self._edit = ""

        if direction:
            if direction > 0:
                self.quote = self.quotes.next()
            else:
                self.quote = self.quotes.previous()
            self.screen.setup_quote(self.quote)
            self.screen.clear()

    def resize(self):
        """Handles a resized terminal."""
        max_y, max_x = self.screen.window.getmaxyx()
        self.screen.clear()

        if hasattr(curses, "resizeterm"):
            # My PyPy version does not have resizeterm, for example.
            curses.resizeterm(max_y, max_x)

        self.screen.setup_quote(self.quote)

    def handle_key(self, key):
        """Dispatches actions based on key and current mode."""
        # TODO: Refactor this mess of a function
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
            self.screen.clear()

            # Render quote anew
            self.screen.show_browser(self.get_stats(self.elapsed))

            # Update first keypress
            self.screen.show_keystroke(self.get_stats(self.elapsed),
                                       self.position,
                                       self.incorrect,
                                       self._edit)

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
