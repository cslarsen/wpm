# -*- encoding: utf-8 -*-

"""
This file is part of the wpm software.
Copyright 2017 Christian Stigen Larsen

Distributed under the GNU GPL v3 or later. See the file LICENSE.txt for the
full license text. This software makes use of open source software.
"""

import argparse
import codecs
import os
import pkg_resources
import sys
import urwid
import wpm
import wpm.game
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

    p.add_argument("--stats-file", default="~/.wpm", type=str,
            help="File to save statistics to")

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

    for timestamp, wpm, acc in games:
        wpms.append(wpm)
        accs.append(acc)

    average_wpm = sum(wpms) / len(wpms)
    average_acc = sum(accs) / len(accs)

    return average_wpm, average_acc

def main():
    opts = parse_args()
    texts = []

    if not os.path.isfile(opts.stats_file):
        stats = wpm.stats.Stats(opts.keyboard)
    else:
        stats = wpm.stats.Stats.load(opts.stats_file)
        if opts.keyboard is not None:
            stats.keyboard = opts.keyboard

    if opts.stats:
        print("Total average: %5.1f" % stats.average())
        for keyboard in sorted(stats.games.keys()):
            print("Keyboard: %s" % (keyboard if keyboard is not None else
                "Unspecified"))

            games = stats.games[keyboard]
            awpm, aacc = averages(games)
            print("   all %4d games: %5.1f average wpm, %4.1f%% average accuracy" % (
                len(games), awpm, 100.0*aacc))

            last_n = 10
            if len(games) >= last_n:
                awpm, aacc = averages(games[-last_n:])
                print("  last %4d games: %5.1f average wpm, %4.1f%% average accuracy" % (
                    last_n, awpm, 100.0*aacc))

        if stats.keyboard is not None:
            print("Current keyboard: %s" % stats.keyboard)
        return

    if opts.load_json is not None:
        texts += wpm.game.load(opts.load_json)

    if opts.load is not None:
        with codecs.open(opts.load, encoding="utf-8") as f:
            text = f.read().replace("\r", "").rstrip()
        texts.append({"author": "", "title": "", "text": text})

    if len(texts) == 0:
        filename = pkg_resources.resource_filename("wpm", "data/examples.json")
        texts = wpm.game.load(filename)

    try:
        game = wpm.game.Game(texts, stats)
        game.set_tab_spaces(opts.tabs)
        game.run()
    except urwid.main_loop.ExitMainLoop:
        pass
    game.stats.save(opts.stats_file)
