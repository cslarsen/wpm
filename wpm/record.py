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

class Recorder(object):
    """Class for recording keystrokes."""
    def __init__(self):
        self.reset()

    def add(self, elapsed, key, position, incorrect):
        """Adds a time stamp."""
        self.elapsed.append(elapsed)
        self.keys.append(key)
        self.position.append((position, incorrect))

    def reset(self):
        """Destroys all time stamps."""
        self.elapsed = collections.deque()
        self.keys = collections.deque()
        self.position = collections.deque()

    def __getitem__(self, index):
        elapsed = self.elapsed[index]
        key = self.keys[index]
        position, incorrect = self.position[index]
        return elapsed, key, position, incorrect

    def __len__(self):
        return len(self.elapsed)

class Playback(object):
    def __init__(self, recorder):
        self.recorder = recorder
        self.index = 0

    def next(self):
        values = self.recorder[self.index]
        self.index = (self.index + 1) % len(self.recorder)
        return values
