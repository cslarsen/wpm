# -*- encoding: utf-8 -*-

"""
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

from wpm.config import Config
from wpm.error import WpmError
from wpm.gauss import confidence_interval

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
        self.config = Config()

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
            raise WpmError(
                "wpm requires at least %d lines in your display" % min_lines)

        min_cols = 20
        if self.columns < min_cols:
            curses.endwin()
            raise WpmError(
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
            self.first_key = True
            self.quote = ""
            self.quote_author = ""
            self.quote_columns = 0
            self.quote_coords = tuple()
            self.quote_height = 0
            self.quote_id = 0
            self.quote_lengths = tuple()
            self.quote_title = ""
        except:
            curses.endwin()
            raise

    @staticmethod
    def _word_wrap(text, width):
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

    @staticmethod
    def _screen_coords(lengths, position):
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
        hicolor = os.getenv("TERM").endswith("256color")

        if hicolor:
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

        if not hicolor:
            # Make certain colors more visible
            Screen.COLOR_CORRECT |= curses.A_DIM
            Screen.COLOR_INCORRECT |= curses.A_UNDERLINE | curses.A_BOLD
            Screen.COLOR_QUOTE |= curses.A_BOLD
            Screen.COLOR_STATUS |= curses.A_BOLD

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

    def chgat(self, x_pos, y_pos, length, color):
        """Wraps call around curses.window.chgat."""
        if self.lines > y_pos >= 0:
            if x_pos >= 0 and (x_pos + length) <= self.columns:
                self.window.chgat(y_pos, x_pos, length, color)

    def set_cursor(self, x_pos, y_pos):
        """Sets cursor position."""
        if (y_pos < self.lines) and (x_pos < self.columns):
            self.window.move(y_pos, x_pos)

    def right_column(self, y_pos, x_pos, width, text):
        """Writes text to screen in coumns."""
        lengths = Screen._word_wrap(text, width)

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
        self.addstr(0, 0, text, Screen.COLOR_STATUS)
        self.chgat(0, 0, self.columns, Screen.COLOR_STATUS)
        #self.window.chgat(0, 0, self.columns, Screen.COLOR_STATUS)

    def set_quote(self, quote):
        """Sets up variables used for a new quote."""
        # TODO: Move this stuff elsewhere
        if self.config.max_quote_width > 0:
            self.quote_columns = min(self.columns, self.config.max_quote_width)
        else:
            self.quote_columns = self.columns

        self.cheight = 0
        self.quote = quote.text
        self.quote_author = quote.author
        self.quote_id = quote.text_id
        self.quote_title = quote.title
        self.quote_lengths = tuple(Screen._word_wrap(self.quote,
                                                     self.quote_columns - 1))
        self.quote_height = len(self.quote_lengths)

        # Remember (x, y) position for each quote offset.
        self.quote_coords = []
        for offset in range(len(self.quote)+1):
            x_pos, y_pos = Screen._screen_coords(self.quote_lengths, offset)
            self.quote_coords.append((x_pos, y_pos))
        self.quote_coords = tuple(self.quote_coords)

    def clear_prompt(self):
        self.set_cursor(0, self.cheight)
        self.window.clrtoeol()

    def update_prompt(self, prompt):
        """Prints prompt on the display."""
        self.addstr(0, self.cheight, (prompt + " ").encode(self.encoding),
                    Screen.COLOR_PROMPT)

    def show_browser(self, head, stats):
        """Show quote browsing screen."""
        self.update_header(head)
        self.update_quote(Screen.COLOR_QUOTE)
        self.update_author()
        self.show_help()
        self.show_stats(stats)
        self.set_cursor(0, 2)

    def show_help(self):
        """Shows help instructions on screen."""
        self.cheight += 1
        self.set_cursor(0, self.cheight)
        self.addstr(0, self.cheight,
                    "Start typing, hit SPACE/ARROWS to browse or ESC to quit.",
                    Screen.COLOR_PROMPT)

    def show_stats(self, stats):
        """Shows statistics for the current quote."""
        results = stats.text_id_results(stats.keyboard, self.quote_id)

        if len(results) < 2:
            return

        percent = self.config.confidence_interval_percent
        alpha = 1 - (percent/100.0)
        samples = len(results)

        wpm_avg, acc_avg = results.averages()
        wpm_sd, acc_sd = results.stddevs()
        wpm_min, wpm_max, acc_min, acc_max = results.extremals()
        wpm_ci0, wpm_ci1 = confidence_interval(wpm_avg, wpm_sd, samples, alpha)
        acc_ci0, acc_ci1 = confidence_interval(acc_avg, acc_sd, samples, alpha)

        msg = "wpm %5.1f min %5.1f avg %5.1f max %5.1f sd [%5.1f-%5.1f] %d%% ci (n=%d)" % (
                wpm_min, wpm_avg, wpm_max, wpm_sd, wpm_ci0, wpm_ci1, percent,
                samples)
        self.cheight += 2
        self.addstr(0, self.cheight, msg, Screen.COLOR_CORRECT)

        msg = "acc %5.1f min %5.1f avg %5.1f max %5.1f sd [%5.1f %5.1f] %d%% ci (n=%d)" % (
                100*acc_min, 100*acc_avg, 100*acc_max, 100*acc_sd, 100*acc_ci0,
                100*acc_ci1, percent, samples)
        self.cheight += 1
        self.addstr(0, self.cheight, msg, Screen.COLOR_CORRECT)
        self.cheight += 1

    def show_score(self, head, wpm_score, stats):
        """Show score screen after typing has finished."""
        self.update_header(head)
        self.update_quote(Screen.COLOR_CORRECT)
        self.update_author()

        # Highlight score
        score = "You scored %.1f wpm!" % wpm_score
        self.update_prompt(score)
        if len(score) < self.columns:
            self.chgat(11, self.cheight, len(str("%.1f" % wpm_score)),
                       Screen.COLOR_HISCORE)

        self.show_help()
        self.show_stats(stats)
        self.set_cursor(0, 2)

    def highlight_progress(self, position, incorrect):
        """Colors finished and incorrectly typed parts of the quote."""
        if incorrect:
            color = Screen.COLOR_INCORRECT
        else:
            color = Screen.COLOR_CORRECT

        # Highlight correct / incorrect character in quote
        ixpos, iypos = self.quote_coords[position + incorrect - 1]
        color = Screen.COLOR_INCORRECT if incorrect else Screen.COLOR_CORRECT
        self.chgat(max(ixpos, 0), 2 + iypos, 1, color)

        # Highlight next as correct, in case of backspace
        xpos, ypos = self.quote_coords[position + incorrect]
        self.chgat(xpos, 2 + ypos, 1, Screen.COLOR_QUOTE)

    def show_keystroke(self, head, position, incorrect, typed, key):
        """Updates the screen while typing."""
        self.update_header(head)

        if key and (position + incorrect) <= len(self.quote):
            self.highlight_progress(position, incorrect)
            self.update_prompt("> " + typed)

        # Move cursor to current position in text before refreshing
        xpos, ypos = self.quote_coords[position + incorrect]
        self.set_cursor(min(xpos, self.quote_columns - 1), 2 + ypos)

    def rerender_race(self, head):
        """Re-renders currently running game."""
        self.clear()
        self.update_header(head)
        self.update_quote(Screen.COLOR_QUOTE)
        self.update_author()
        self.set_cursor(0, 2)

    def clear(self):
        """Clears the screen."""
        self.window.clear()

    def deinit(self):
        """Deinitializes curses."""
        curses.nocbreak()
        self.screen.keypad(False)
        curses.echo()
        curses.endwin()
