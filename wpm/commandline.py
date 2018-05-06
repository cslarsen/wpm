# -*- encoding: utf-8 -*-

"""
This file is part of the wpm software.
Copyright 2017, 2018 Christian Stigen Larsen

Distributed under the GNU Affero General Public License (AGPL) v3 or later. See
the file LICENSE.txt for the full license text. This software makes use of open
source software.

The quotes database is *not* covered by the AGPL!
"""

import argparse
import codecs
import os
import sys

from wpm.gauss import confidence_interval
import wpm
import wpm.config
import wpm.error
import wpm.game
import wpm.quotes
import wpm.stats

def parse_args():
    """Parses command line arguments."""
    argp = argparse.ArgumentParser(prog="wpm", epilog=wpm.__copyright__)

    argp.add_argument("--load-json", metavar="FILENAME", default=None,
                      help="""JSON file containing quotes.

The format is

[{"author": "...", "title": "...", "text": "...", "id": ...}, ...]
""")
    argp.add_argument("--load", metavar="FILENAME", default=None,
                      help="A pure text file to train on.")

    argp.add_argument("-V", "--version", default=False, action="store_true",
                      help="Show program version")

    argp.add_argument("--keyboard", default=None, type=str,
                      help="Records WPM statistics under the given keyboard name")

    argp.add_argument("-s", "--stats", default=False, action="store_true",
                      help="Shows keyboard statistics")

    argp.add_argument("--stats-file", default="~/.wpm.csv", type=str,
                      help="File to record score history to (CSV format)")

    argp.add_argument("--id", "-i", default=None, type=int,
                      help="If specified, jumps to given text ID on start.")

    argp.add_argument("--search", default=None, type=str,
                      help="Put quotes/authors/titles matching case-insensitive text query first")

    opts = argp.parse_args()

    if opts.version:
        print("WPM v%s" % wpm.__version__)
        print(wpm.__copyright__)
        print("Source code (sans quotes) distributed under the %s" % wpm.__license__)
        sys.exit(0)

    opts.stats_file = os.path.expanduser(opts.stats_file)
    return opts

def load_stats(filename, keyboard):
    """Loads CSV stats from file."""
    if not os.path.isfile(filename):
        return wpm.stats.Stats(keyboard)

    try:
        stats = wpm.stats.Stats.load(filename)
    except ValueError:
        new_name = filename + ".old"
        print("Unsupported format. Renaming %s to %s" % (filename,
                                                         new_name))
        os.rename(filename, new_name)
        stats = wpm.stats.Stats()

    if keyboard is not None:
        stats.keyboard = keyboard

    return stats

def load_json_quotes(filename):
    """Loads quotes from JSON file."""
    if filename is not None:
        return wpm.quotes.Quotes.load_json(filename)
    return []

def load_plain_text_quote(quotes, filename):
    """Loads quotes from plain text file."""
    if not os.path.isfile(filename):
        raise wpm.error.WpmError("No such file: %s" % filename)

    with codecs.open(filename, encoding="utf-8") as file_obj:
        text = file_obj.read()
        text = text.replace("\r", "").rstrip()

        author = ""
        title = os.path.basename(filename)
        database = "plaintext"

        # For now, just use inode for the text ID
        text_id = os.stat(filename).st_ino

        quotes.append([author, title, text, text_id])
        return wpm.quotes.Quotes(quotes, database=database)

def print_stats(stats):
    """Prints table of game results."""
    table = []

    config = wpm.config.Config()
    percent = config.confidence_interval_percent

    for keyboard in sorted(stats.games.keys()):
        name = keyboard if keyboard is not None else "n/a"

        for last_n in [0, 10, 50, 100, 500, 1000]:
            results = stats.results(keyboard, last_n=last_n)

            if len(results) >= last_n:
                if last_n == 0:
                    label = len(results)
                else:
                    label = "n-%d" % last_n

                wpm_avg, acc_avg = results.averages()
                wpm_sd, acc_sd = results.stddevs()

                alpha = 1 - (percent/100.0)
                wpm_ci = confidence_interval(wpm_avg, wpm_sd, len(results), alpha)

                table.append([name,
                              label,
                              wpm_avg,
                              wpm_sd,
                              100.0*acc_avg,
                              100.0*acc_sd,
                              wpm_ci[0],
                              wpm_ci[1]])

    if table:
        width = max(max(len(e[0]) for e in table), 11)
    else:
        width = 0

    print("Keyboard     Games   WPM                        Accuracy")
    print("                     average stddev %d%% ci      average stddev" % percent)

    for entry in table:
        label, count, wpm_avg, wpm_sd, acc_avg, acc_sd, ci0, ci1 = entry
        print("%-*s   %5s  %5.1f  %5.1f   %5.1f-%5.1f %5.1f%%  %5.1f%%" %
              (width, label, count, wpm_avg, wpm_sd, ci0, ci1, acc_avg, acc_sd))

def search(quotes, query):
    """Returns text IDs for quotes matching query."""
    for quote in iter(quotes):
        quote = wpm.quotes.Quote.from_tuple(quote)

        author = quote.author.lower()
        title = quote.title.lower()
        text = quote.text.lower()

        if (query in text) or (query in author) or (query in title):
            yield quote.text_id

def main():
    """Main entry point for command line invocation."""
    try:
        opts = parse_args()
        stats = load_stats(opts.stats_file, opts.keyboard)

        if opts.load_json is not None:
            quotes = load_json_quotes(opts.load_json)
        elif opts.load is not None:
            quotes = load_plain_text_quote([], opts.load)
        else:
            # Load default database
            quotes = wpm.quotes.Quotes.load()

        if opts.stats:
            print_stats(stats)
            return

        if opts.search:
            text_ids = list(search(quotes, opts.search.lower()))

            if not text_ids:
                print("No quotes matching %r" % opts.search)
                sys.exit(1)
        elif opts.id is not None:
            text_ids = [opts.id]
        else:
            text_ids = []
    except wpm.error.WpmError as error:
        print(error)
        sys.exit(1)

    with wpm.game.GameManager(quotes, stats) as gm:
        try:
            gm.run(to_front=text_ids)
            gm.stats.save(opts.stats_file)
        except KeyboardInterrupt:
            gm.stats.save(opts.stats_file)
            sys.exit(0)
