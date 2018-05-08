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
import csv
import datetime
import math
import os

class Timestamp(object):
    """Methods for dealing with timestamps."""
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

    @staticmethod
    def from_string(string):
        """Parses timestamp from string in ``Timestamp.DATETIME_FORMAT``."""
        return datetime.datetime.strptime(string, Timestamp.DATETIME_FORMAT)

    @staticmethod
    def now():
        """Returns current UTC time."""
        return datetime.datetime.utcnow()


class GameResult(object):
    """Contains the result of one game."""
    # pylint: disable=too-many-instance-attributes, too-few-public-methods

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

    def __repr__(self):
        return "<GameResult: %s wpm=%.1f acc=%.1f id=%d>" % (
                self.timestamp, self.wpm, self.accuracy, self.text_id)


class GameResults(object):
    """Container for several GameResult objects."""
    def __init__(self, tag, games):
        self.tag = tag
        self.games = games

    @property
    def results(self):
        """Yields all the ``GameResult`` objects."""
        for game in self.games:
            yield GameResult(game)

    def __repr__(self):
        return "<GameResults: len=%d tag=%r>" % (len(self.games), self.tag)

    def append(self, game):
        self.games.append(game)

    def __len__(self):
        return len(self.games)

    def extremals(self):
        init = 999999
        min_wpm = init
        max_wpm = 0
        min_acc = init
        max_acc = 0

        for result in self.results:
            min_wpm = min(min_wpm, result.wpm)
            max_wpm = max(max_wpm, result.wpm)
            min_acc = min(min_acc, result.accuracy)
            max_acc = max(max_acc, result.accuracy)

        if min_wpm == init:
            min_wpm = 0
        if min_acc == init:
            min_acc = 0

        return min_wpm, max_wpm, min_acc, max_acc

    def averages(self):
        """Returns a tuple of WPM and accuracy averages."""
        if not self.games:
            return 0, 0

        wpms = 0
        accs = 0

        for result in self.results:
            wpms += result.wpm
            accs += result.accuracy

        return wpms / len(self), accs / len(self)

    def stddevs(self):
        """Returns a tuple of WPM and accuracy standard deviations.

        Calculated from the root of the sample variance.
        """
        samples = len(self)

        if samples <= 1:
            return 0.0, 0.0

        wpm_sd = 0
        acc_sd = 0

        wpm_avg, acc_avg = self.averages()

        for result in self.results:
            wpm_sd += (result.wpm - wpm_avg)**2.0
            acc_sd += (result.accuracy - acc_avg)**2.0

        return (math.sqrt(wpm_sd/(samples - 1)),
                math.sqrt(acc_sd/(samples - 1)))


class Stats(object):
    """Typing statistics"""
    def __init__(self, current_tag=None, games=None):
        self.tag = current_tag
        if games is None:
            self.games = collections.defaultdict(list)
        else:
            self.games = games

    def __repr__(self):
        return "<Stats: tag=%d current=%r>" % (len(self), self.tag)

    def results(self, tag=None, last_n=0):
        """Returns the ``GameResults``."""
        if tag is None:
            tag = self.tag
        return GameResults(tag, self.games[tag][-last_n:])

    def text_id_results(self, tag, text_id):
        results = GameResults(self.tag, [])

        for game in self.games[tag]:
            if game[5] == text_id:
                results.append(game)

        return results

    def add(self, wpm, accuracy, text_id, database):
        """Adds a game result to the stats."""
        race = 0
        rank = 1
        racers = 1

        self.games[self.tag].append((
            race,
            wpm,
            accuracy,
            rank,
            racers,
            text_id,
            Timestamp.now(),
            database))

    def average(self, tag=None, last_n=None):
        """Returns the average WPM."""
        return self.results(tag, last_n).averages()[0]

    def __len__(self):
        return len(self.games)

    def __getitem__(self, key):
        return self.games[key]

    def keys(self):
        """Returns keys for this dict-like object."""
        return self.games.keys()

    def values(self):
        """Returns values for this dict-like object."""
        return self.games.values()

    def items(self):
        """Returns tuple of keys and values for this dict-like object."""
        return self.games.items()

    @staticmethod
    def load(filename=None):
        """Loads stats from a CSV file."""

        if filename is None:
            filename = os.path.expanduser("~/.wpm.csv")

        games = collections.defaultdict(list)
        current_tag = None

        def parse(row):
            """Converts CSV row to internal types."""
            race = int(row[0])
            wpm = float(row[1])
            accuracy = float(row[2])
            rank = int(row[3])
            racers = int(row[4])
            text_id = int(row[5])
            timestamp = Timestamp.from_string(row[6])
            database = row[7]
            tag = row[8]

            return (race, wpm, accuracy, rank, racers, text_id, timestamp,
                    database, tag)

        with open(filename, "rt") as file_obj:
            reader = csv.reader(file_obj)

            for row in reader:
                result = parse(row)
                tag = result[-1]
                games[tag].append(result[:-1])
                current_tag = tag

        return Stats(current_tag, games)

    def save(self, filename):
        """Writes game results to a CSV file compatible with the one from
        TypeRacer."""
        allgames = []
        for tag, games in self.items():
            if tag is None:
                tag = "Unspecified"

            for game in games:
                allgames.append(list(game) + [tag])

        by_time = lambda row: row[6]
        games = sorted(allgames, key=by_time)

        # Write to a temp file just in case we get an exception
        with open(filename + ".tmp", "wt") as file_obj:
            writer = csv.writer(file_obj)

            for race, game in enumerate(games):
                # The timestamp is the race number, so use that instead.
                game[0] = 1 + race
                writer.writerow(game)

        os.rename(filename + ".tmp", filename)
