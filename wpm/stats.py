# -*- encoding: utf-8 -*-

"""
This file is part of the wpm software.
Copyright 2017 Christian Stigen Larsen

Distributed under the GNU GPL v3 or later. See the file LICENSE.txt for the
full license text. This software makes use of open source software.
"""
import datetime
import pickle

class Stats(object):
    """Typing statistics"""

    def __init__(self, current_keyboard=None):
        self.keyboard = current_keyboard
        self.games = {}

    def add(self, wpm, accuracy):
        if self.keyboard not in self.games:
            self.games[self.keyboard] = []

        self.games[self.keyboard].append((
            datetime.datetime.now(),
            wpm,
            accuracy))

    def average(self, keyboard=None, last_n=None):
        total = []

        for kbd in self.games.keys():
            if keyboard is not None:
                if kbd != keyboard:
                    continue
            for stamp, wpm, acc in self.games[kbd]:
                total.append(wpm)

        if (last_n is not None) and len(total) >= last_n:
            total = total[-last_n:]

        if len(total) > 0:
            return sum(total) / len(total)
        else:
            return 0

    @staticmethod
    def load(filename):
        with open(filename, "rb") as f:
            return pickle.load(f)

    def save(self, filename):
        with open(filename, "wb") as f:
            pickle.dump(self, f, protocol=0)
