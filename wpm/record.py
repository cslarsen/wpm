# -*- encoding: utf-8 -*-

"""
This file is part of the wpm software.
Copyright 2017, 2018 Christian Stigen Larsen

Distributed under the GNU Affero General Public License (AGPL) v3 or later. See
the file LICENSE.txt for the full license text. This software makes use of open
source software.

The quotes database is *not* covered by the AGPL!
"""

import collections

class TimeRecorder(object):
    """Class for recording keystrokes."""
    def __init__(self):
        self.reset()

    def add(self, elapsed, key):
        """Adds a time stamp."""
        self.values.append(elapsed)
        self.keys.append(key)

    def reset(self):
        """Destroys all time stamps."""
        self.values = collections.deque()
        self.keys = collections.deque()
