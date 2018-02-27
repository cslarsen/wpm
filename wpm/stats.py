# -*- encoding: utf-8 -*-

"""
This file is part of the wpm software.
Copyright 2018 Christian Stigen Larsen

Distributed under the GNU GPL v3 or later. See the file LICENSE.txt for the
full license text. This software makes use of open source software.
"""

import collections
import csv
import datetime
import os

class Timestamp(object):
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

    @staticmethod
    def from_string(string):
        return datetime.datetime.strptime(string, Timestamp.DATETIME_FORMAT)

    @staticmethod
    def now():
        return datetime.datetime.utcnow()


class Stats(object):
    """Typing statistics"""

    def __init__(self, current_keyboard=None):
        self.keyboard = current_keyboard
        self.games = collections.defaultdict(list)

    def add(self, wpm, accuracy, text_id, database):
        race = 0
        rank = 1
        racers = 1

        self.games[self.keyboard].append((
            race,
            wpm,
            accuracy,
            rank,
            racers,
            text_id,
            Timestamp.now(),
            database))

    def average(self, keyboard=None, last_n=None):
        total = []

        for kbd in self.games.keys():
            if keyboard is not None:
                if kbd != keyboard:
                    continue
            for game in self.games[kbd]:
                total.append(game[1])

        if (last_n is not None) and len(total) >= last_n:
            total = total[-last_n:]

        if len(total) > 0:
            return sum(total) / len(total)
        else:
            return 0

    def __len__(self):
        return len(self.games)

    def __getitem__(self, key):
        return self.games[key]

    def keys(self):
        return self.games.keys()

    def values(self):
        return self.games.values()

    def items(self):
        return self.games.items()

    @staticmethod
    def load(filename):
        games = collections.defaultdict(list)
        current_keyboard = None

        with open(filename, "rt") as f:
            reader = csv.reader(f)
            for row in reader:
                race = int(row[0])
                wpm = float(row[1])
                accuracy = float(row[2])
                rank = int(row[3])
                racers = int(row[4])
                text_id = int(row[5])
                timestamp = Timestamp.from_string(row[6])
                database = row[7]
                keyboard = row[8]

                if keyboard not in games:
                    games[keyboard] = []
                games[keyboard].append((race, wpm, accuracy, rank, racers,
                    text_id, timestamp, database))
                current_keyboard = keyboard

        stats = Stats(current_keyboard)
        stats.games = games
        return stats

    def save(self, filename):
        """Writes game results to a CSV file compatible with the one from
        TypeRacer."""
        allgames = []
        for keyboard, games in self.items():
            if keyboard is None:
                keyboard = "Unspecified"

            for game in games:
                allgames.append(list(game) + [keyboard])

        by_time = lambda row: row[6]
        games = sorted(allgames, key=by_time)

        # Write to a temp file just in case we get an exception
        with open(filename + ".tmp", "wt") as f:
            writer = csv.writer(f)

            for race, game in enumerate(games):
                # The timestamp is the race number, so use that instead.
                game[0] = 1 + race
                writer.writerow(game)

        os.rename(filename + ".tmp", filename)
