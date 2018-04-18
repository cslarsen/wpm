# -*- encoding: utf-8 -*-

"""
This file is part of the wpm software.
Copyright 2017 Christian Stigen Larsen

Distributed under the GNU AGPL v3 or later. See the file LICENSE.txt for the
full license text. This software makes use of open source software.
"""

import collections
import csv
import datetime
import math
import os

class Timestamp(object):
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

    @staticmethod
    def from_string(string):
        return datetime.datetime.strptime(string, Timestamp.DATETIME_FORMAT)

    @staticmethod
    def now():
        return datetime.datetime.utcnow()


class GameResult(object):
    def __init__(self, game):
        race, wpm, accuracy, rank, racers, text_id, timestamp, database = game
        self.race = race
        self.wpm = wpm
        self.accuracy = accuracy
        self.rank = rank
        self.racers = racers
        self.text_id = text_id
        self.timestamp = timestamp
        self.database = database


class GameResults(object):
    def __init__(self, keyboard, games):
        self.keyboard = keyboard
        self.games = games

    @property
    def results(self):
        for game in self.games:
            yield GameResult(game)

    def __len__(self):
        return len(self.games)

    def averages(self):
        if len(self) == 0:
            return 0, 0

        wpms = 0
        accs = 0

        for result in self.results:
            wpms += result.wpm
            accs += result.accuracy

        return wpms / len(self), accs / len(self)

    def stddevs(self):
        n = len(self)

        if n <= 1:
            return 0.0, 0.0

        wpm_sd = 0
        acc_sd = 0

        wpm_avg, acc_avg = self.averages()

        for result in self.results:
            wpm_sd += (result.wpm - wpm_avg)**2.0
            acc_sd += (result.accuracy - acc_avg)**2.0

        return math.sqrt(wpm_sd/(n-1)), math.sqrt(acc_sd/(n-1))


class Stats(object):
    """Typing statistics"""
    def __init__(self, current_keyboard=None, games=None):
        self.keyboard = current_keyboard
        if games is None:
            self.games = collections.defaultdict(list)
        else:
            self.games = games

    def results(self, keyboard, last_n=0):
        return GameResults(keyboard, self.games[keyboard][-last_n:])

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
        wpm_avg, acc_avg = self.results(keyboard, last_n).averages()
        return wpm_avg

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

        return Stats(current_keyboard, games)

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
