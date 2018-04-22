"""
Code for dealing with user configuration settings (rc-file).

This file is part of the wpm software.
Copyright 2017, 2018 Christian Stigen Larsen

Distributed under the GNU Affero General Public License (AGPL) v3 or later. See
the file LICENSE.txt for the full license text. This software makes use of open
source software.

The quotes database is *not* covered by the AGPL!
"""

import curses
import os
import sys

try:
    import configparser
except ImportError:
    # Python 2.7
    import ConfigParser as configparser

class Config(object):
    """Contains the user configuration, backed by the .wpmrc file."""
    # pylint: disable=too-many-public-methods

    config = None

    def __init__(self):
        Config.config = configparser.ConfigParser()
        self.filename = os.path.expanduser("~/.wpmrc")

        if os.path.isfile(self.filename):
            self.load()
        else:
            Config.set_defaults()
            self.save()

    def load(self):
        """Loads ~/.wpmrc config settings."""
        Config.config.read(self.filename)

    def save(self):
        """Saves settings to ~/.wpmrc"""
        with open(self.filename, "wt") as file_obj:
            Config.config.write(file_obj)

    @staticmethod
    def set_defaults():
        """Sets up default settings."""
        Config.config.add_section("curses")
        Config.config.set("curses", "escdelay", "15")
        Config.config.set("curses", "window_timeout", "20")

        Config.config.add_section("wpm")
        Config.config.set("wpm", "max_quote_width", "-1")

        Config.config.add_section("xterm-256color")
        Config.config.set("xterm-256color", "author_bg", str(233))
        Config.config.set("xterm-256color", "author_fg", str(240))
        Config.config.set("xterm-256color", "background", str(233))
        Config.config.set("xterm-256color", "correct_bg", str(233))
        Config.config.set("xterm-256color", "correct_fg", str(240))
        Config.config.set("xterm-256color", "incorrect_bg", str(52))
        Config.config.set("xterm-256color", "incorrect_fg", str(197))
        Config.config.set("xterm-256color", "prompt_bg", str(233))
        Config.config.set("xterm-256color", "prompt_fg", str(244))
        Config.config.set("xterm-256color", "quote_bg", str(233))
        Config.config.set("xterm-256color", "quote_fg", str(195))
        Config.config.set("xterm-256color", "score_highlight_bg", str(197))
        Config.config.set("xterm-256color", "score_highlight_fg", str(230))
        Config.config.set("xterm-256color", "status_bg", str(24))
        Config.config.set("xterm-256color", "status_fg", str(51))

        Config.config.add_section("xterm-colors")
        Config.config.set("xterm-colors", "author_bg", str(curses.COLOR_BLACK))
        Config.config.set("xterm-colors", "author_fg", str(curses.COLOR_WHITE))
        Config.config.set("xterm-colors", "background", str(curses.COLOR_BLACK))
        Config.config.set("xterm-colors", "correct_bg", str(curses.COLOR_BLACK))
        Config.config.set("xterm-colors", "correct_fg", str(curses.COLOR_WHITE))
        Config.config.set("xterm-colors", "incorrect_bg", str(curses.COLOR_RED))
        Config.config.set("xterm-colors", "incorrect_fg", str(curses.COLOR_WHITE))
        Config.config.set("xterm-colors", "prompt_bg", str(curses.COLOR_BLACK))
        Config.config.set("xterm-colors", "prompt_fg", str(curses.COLOR_WHITE))
        Config.config.set("xterm-colors", "quote_bg", str(curses.COLOR_BLACK))
        Config.config.set("xterm-colors", "quote_fg", str(curses.COLOR_WHITE))
        Config.config.set("xterm-colors", "score_highlight_bg", str(curses.COLOR_RED))
        Config.config.set("xterm-colors", "score_highlight_fg", str(curses.COLOR_YELLOW))
        Config.config.set("xterm-colors", "status_bg", str(curses.COLOR_BLUE))
        Config.config.set("xterm-colors", "status_fg", str(curses.COLOR_CYAN))

    @property
    def escdelay(self):
        """Curses ESCDELAY."""
        return Config.config.get("curses", "escdelay")

    @property
    def window_timeout(self):
        """Curses window timeout."""
        return int(Config.config.get("curses", "window_timeout"))

    @property
    def max_quote_width(self):
        """Length to wrap quotes at. Inactive if zero or less."""
        try:
            return int(Config.config.get("wpm", "max_quote_width"))
        except configparser.NoSectionError:
            Config.config.add_section("wpm")
            Config.config.set("wpm", "max_quote_width", 0)

    @property
    def background_color_256(self):
        """Background color for 256-color terminalss."""
        return int(Config.config.get("xterm-256color", "background"))

    @property
    def incorrect_color_256(self):
        """Incorrectly type quote color for 256-color terminals."""
        return (int(Config.config.get("xterm-256color", "incorrect_fg")),
                int(Config.config.get("xterm-256color", "incorrect_bg")))

    @property
    def status_color_256(self):
        """Top status bar color for 256-color terminals."""
        return (int(Config.config.get("xterm-256color", "status_fg")),
                int(Config.config.get("xterm-256color", "status_bg")))

    @property
    def correct_color_256(self):
        """Color for correctly typed text for 256-color terminals."""
        return (int(Config.config.get("xterm-256color", "correct_fg")),
                int(Config.config.get("xterm-256color", "correct_bg")))

    @property
    def quote_color_256(self):
        """Quote color for 256-color terminals."""
        return (int(Config.config.get("xterm-256color", "quote_fg")),
                int(Config.config.get("xterm-256color", "quote_bg")))

    @property
    def author_color_256(self):
        """Author color for 256-color terminals."""
        return (int(Config.config.get("xterm-256color", "author_fg")),
                int(Config.config.get("xterm-256color", "author_bg")))

    @property
    def prompt_color_256(self):
        """Prompt, or input, color for 256-color terminals."""
        return (int(Config.config.get("xterm-256color", "prompt_fg")),
                int(Config.config.get("xterm-256color", "prompt_bg")))

    @property
    def score_highlight_color_256(self):
        """Highlighted score color for 256-color displays."""
        return (int(Config.config.get("xterm-256color", "score_highlight_fg")),
                int(Config.config.get("xterm-256color", "score_highlight_bg")))

    @property
    def background_color(self):
        """Background color."""
        return int(Config.config.get("xterm-colors", "background"))

    @property
    def incorrect_color(self):
        """Color of incorrectly typed text."""
        return (int(Config.config.get("xterm-colors", "incorrect_fg")),
                int(Config.config.get("xterm-colors", "incorrect_bg")))

    @property
    def status_color(self):
        """Top status bar color."""
        return (int(Config.config.get("xterm-colors", "status_fg")),
                int(Config.config.get("xterm-colors", "status_bg")))

    @property
    def correct_color(self):
        """Color for correctly typed text."""
        return (int(Config.config.get("xterm-colors", "correct_fg")),
                int(Config.config.get("xterm-colors", "correct_bg")))

    @property
    def quote_color(self):
        """Normal color for quote."""
        return (int(Config.config.get("xterm-colors", "quote_fg")),
                int(Config.config.get("xterm-colors", "quote_bg")))

    @property
    def author_color(self):
        """Color for author."""
        return (int(Config.config.get("xterm-colors", "author_fg")),
                int(Config.config.get("xterm-colors", "author_bg")))

    @property
    def prompt_color(self):
        """Color for the input field."""
        return (int(Config.config.get("xterm-colors", "prompt_fg")),
                int(Config.config.get("xterm-colors", "prompt_bg")))

    @property
    def score_highlight_color(self):
        """Highlighted score color."""
        return (int(Config.config.get("xterm-colors", "score_highlight_fg")),
                int(Config.config.get("xterm-colors", "score_highlight_bg")))
