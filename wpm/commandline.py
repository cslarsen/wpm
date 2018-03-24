# -*- encoding: utf-8 -*-

"""
This file is part of the wpm software.
Copyright 2017 Christian Stigen Larsen

Distributed under the GNU GPL v3 or later. See the file LICENSE.txt for the
full license text. This software makes use of open source software.
"""

import argparse
import codecs
import math
import os
import sys
import wpm
import wpm.error
import wpm.game
import wpm.quotes
import wpm.stats

def parse_args():
    p = argparse.ArgumentParser(prog="wpm", epilog=wpm.__copyright__)

    p.add_argument("--load-json", metavar="FILENAME", default=None,
            help="""JSON file containing texts to train on.

The format is

[{"author": "...", "title": "...", "text": "..."}, ...]
""")
    p.add_argument("--load", metavar="FILENAME", default=None,
            help="A pure text file to train on.")

    p.add_argument("-V", "--version", default=False, action="store_true",
            help="Show program version")

    p.add_argument("--tabs", default=None, type=int,
            help="If set, expand tabs to this number of spaces")

    p.add_argument("--keyboard", default=None, type=str,
            help="Records WPM statistics under the given keyboard name")

    p.add_argument("-s", "--stats", default=False, action="store_true",
            help="Shows keyboard statistics")

    p.add_argument("--stats-file", default="~/.wpm.csv", type=str,
            help="File to record score history to (CSV format)")

    p.add_argument("--id", "-i", default=None, type=int,
            help="If specified, jumps to given text ID on start.")

    opts = p.parse_args()

    if opts.version:
        print("WPM v%s" % wpm.__version__)
        print(wpm.__copyright__)
        print("Distributed under the %s" % wpm.__license__)
        sys.exit(0)

    opts.stats_file = os.path.expanduser(opts.stats_file)
    return opts

def averages(games):
    wpms = []
    accs = []

    # TODO: Fix this
    for game in games:
        wpm = game[1]
        wpms.append(wpm)

        accuracy = game[2]
        accs.append(accuracy)

    average_wpm = sum(wpms) / len(wpms)
    average_acc = sum(accs) / len(accs)

    return average_wpm, average_acc

def stddevs(games):
    awpm, aacc = averages(games)
    n = len(games)

    if n <= 1:
        return 0, 0

    swpm = 0
    sacc = 0
    for game in games:
        wpm = game[1]
        acc = game[2]
        swpm += (wpm - awpm)**2.0
        sacc += (acc - aacc)**2.0

    return math.sqrt(swpm/(n-1)), math.sqrt(sacc/(n-1))

def main():
    opts = parse_args()
    quotes = []

    if not os.path.isfile(opts.stats_file):
        stats = wpm.stats.Stats(opts.keyboard)
    else:
        try:
            stats = wpm.stats.Stats.load(opts.stats_file)
        except Exception as e:
            print("Unsupported format. Renaming %s to %s" % (opts.stats_file,
                opts.stats_file + ".old"))
            os.rename(opts.stats_file, opts.stats_file + ".old")
            stats = wpm.stats.Stats()

        if opts.keyboard is not None:
            stats.keyboard = opts.keyboard

    if opts.load_json is not None:
        quotes = wpm.quotes.Quotes.load_json(opts.load_json)

    if opts.load is not None:
        with codecs.open(opts.load, encoding="utf-8") as f:
            text = f.read().replace("\r", "").rstrip()
        quotes.append(["", "", text])

        quotes = wpm.quotes.Quotes(quotes)

    if opts.stats:
        table = []
        for keyboard in sorted(stats.games.keys()):
            name = keyboard if keyboard is not None else "Unspecified"

            games = stats.games[keyboard]
            awpm, aacc = averages(games)
            swpm, sacc = stddevs(games)

            for last_n in [0, 10, 100, 1000]:
                if len(games) >= last_n:
                    if last_n == 0:
                        label = len(games)
                    else:
                        label = "n-%d" % last_n

                    awpm, aacc = averages(games[-last_n:])
                    swpm, sacc = stddevs(games[-last_n:])

                    table.append([name, label, awpm, swpm, 100.0*aacc, 100.0*sacc])

        width = max(max(len(e[0]) for e in table), 11)
        print("Keyboard      Games    WPM avg stddev     Accuracy avg stddev")
        print("-------------------------------------------------------------")
        for entry in table:
            label, count, wpm_avg, wpm_sd, acc_avg, acc_sd = entry
            print("%-*s   %5s      %5.1f  %5.1f            %4.1f%% %5.1f%%" %
                    (width, label, count, wpm_avg, wpm_sd, acc_avg, acc_sd))
        return

    try:
        if len(quotes) == 0:
            quotes = wpm.quotes.Quotes.load()

        with wpm.game.Game(quotes, stats) as game:
            game.set_tab_spaces(opts.tabs)
            if opts.id is not None:
                try:
                    game.jump_to(opts.id)
                except KeyError as e:
                    raise wpm.error.WpmError("Text ID %d not found" % opts.id)
                    sys.exit(1)
            game.run()
    except KeyboardInterrupt:
        game.stats.save(opts.stats_file)
        sys.exit(0)
    except wpm.error.WpmError as e:
        print(e)
        sys.exit(1)
