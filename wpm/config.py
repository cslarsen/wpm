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

try:
    import configparser
except ImportError:
    # Python 2.7
    import ConfigParser as configparser

from wpm.error import ConfigError

def int_tuple(s):
    """Parses a string containing a tuple of two ints."""
    try:
        if (s[0] != "(") or (s[-1] != ")"):
            raise ValueError()

        values = s[1:-1].split(",")

        if len(values) != 2:
            raise ValueError()

        return map(int, values)
    except ValueError:
        raise ConfigError("Required format is (integer, integer): %s" % s)

DEFAULTS = {
    "curses": {
        "escdelay": (str, 15, "Curses ESCDELAY"),
        "window_timeout": (int, 20, "Curses window timeout"),
    },

    "wpm": {
        "confidence_level": (float, 0.95, "Confidence level for statistics from 0.0 to 1.0"),
        "wrap_width": (int, -1, "Wrap text to this width"),
        "tab_spaces": (int, 1, "Expand tabs to N spaces"),
        "cpm": (int, 0, "Report CPM instead of WPM in stats"),
    },

    "xterm256colors": {
        "author": (int_tuple, (240, 233), ""),
        "background": (int, 233, ""),
        "correct": (int_tuple, (240, 233), ""),
        "incorrect": (int_tuple, (197, 52), ""),
        "prompt": (int_tuple, (244, 233), ""),
        "quote": (int_tuple, (195, 233), ""),
        "score": (int_tuple, (230, 197), ""),
        "top_bar": (int_tuple, (51, 24), ""),
    },

    "xtermcolors": {
        "author": (int_tuple, (curses.COLOR_WHITE, curses.COLOR_BLACK), ""),
        "background": (int, curses.COLOR_BLACK, ""),
        "correct": (int_tuple, (curses.COLOR_WHITE, curses.COLOR_BLACK), ""),
        "incorrect": (int_tuple, (curses.COLOR_RED, curses.COLOR_BLACK), ""),
        "prompt": (int_tuple, (curses.COLOR_WHITE, curses.COLOR_BLACK), ""),
        "quote": (int_tuple, (curses.COLOR_WHITE, curses.COLOR_BLACK), ""),
        "score": (int_tuple, (curses.COLOR_YELLOW, curses.COLOR_RED), ""),
        "top_bar": (int_tuple, (curses.COLOR_CYAN, curses.COLOR_BLUE), ""),
    },
}

class SectionValues(object):
    """Option values for a given section."""
    def __init__(self, section):
        if section not in DEFAULTS.keys():
            raise KeyError(section)
        self.section = section

    def __getattr__(self, name):
        options = DEFAULTS[self.section]
        convert, default, doc = options[name]
        value = Config.config.get(self.section, name)
        try:
            return convert(value)
        except ConfigError as e:
            raise ConfigError("Error in .wpmrc section %r option %r: %s" %
                    (self.section, name, e))


class Config(object):
    """Contains the user configuration, backed by the .wpmrc file."""
    # pylint: disable=too-many-public-methods

    config = None

    def __init__(self):
        Config.config = configparser.ConfigParser()
        self.filename = os.path.expanduser("~/.wpmrc")

        if os.path.isfile(self.filename):
            self.load()
            self.add_defaults()
            self.verify()
        else:
            self.add_defaults()
            self.save()

    def verify(self):
        """Verifies wpmrc values."""
        level = self.wpm.confidence_level
        if not (0 < level < 1):
            raise ConfigError("The .wpmrc confidence level must be within [0, 1>")

    def load(self):
        """Loads ~/.wpmrc config settings."""
        Config.config.read(self.filename)

    def save(self):
        """Saves settings to ~/.wpmrc"""
        with open(self.filename, "wt") as file_obj:
            Config.config.write(file_obj)

    def add_defaults(self):
        """Adds missing sections and options to your ~/.wpmrc file."""
        for section, values in sorted(DEFAULTS.items()):
            if not Config.config.has_section(section):
                Config.config.add_section(section)

            for name, (type, default, doc) in sorted(values.items()):
                if not Config.config.has_option(section, name):
                    Config.config.set(section, name, str(default))

    def __getattr__(self, section):
        """Returns object to look up section options."""
        return SectionValues(section)
