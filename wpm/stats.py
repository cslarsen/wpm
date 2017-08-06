import collections
import datetime
import pickle

class Stats(object):
    """Typing statistics"""

    def __init__(self, current_keyboard=None):
        self.games = collections.defaultdict(list)
        self.keyboard = current_keyboard

    def add(self, wpm, accuracy):
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

        if last_n is not None:
            total = total[-last_n:]

        if len(total) > 0:
            return sum(total) / len(total)
        else:
            return 0

    @staticmethod
    def load(filename):
        with open(filename, "rt") as f:
            return pickle.load(f)

    def save(self, filename):
        with open(filename, "wt") as f:
            pickle.dump(self, f)
