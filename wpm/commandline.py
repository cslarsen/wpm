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
import math
import os
import random
import sys

from wpm.convert import wpm_to_cpm
from wpm.gauss import (prediction_interval, confidence_interval)
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

    argp.add_argument("--tag", default=None, type=str,
                      help="Tag your race scores with this free text field.")

    argp.add_argument("-s", "--stats", default=False, action="store_true",
                      help="Shows score statistics grouped by tags")

    argp.add_argument("--cpm", default=False, action="store_true",
                      help="Shows CPM instead of WPM in stats")

    argp.add_argument("--stats-file", default="~/.wpm.csv", type=str,
                      help="File to record score history to (CSV format)")

    argp.add_argument("--id", "-i", default=None, type=int,
                      help="If specified, jumps to given text ID on start.")

    argp.add_argument("--search", default=None, type=str,
                      help="Put quotes/authors/titles matching case-insensitive text query first")

    argp.add_argument("--short", default=False, action="store_true",
                      help="Starts wpm with short texts")

    argp.add_argument("--monochrome", default=False, action="store_true",
                      help="Starts wpm with monochrome colors")
                    
    argp.add_argument("--redlist", default=False, action="store_true",
                      help="Starts wpm with redlisted texts. To redlist a text, press the \"up\" arrow key. To remove a texts from the redlist, complete each text fast enough or run wpm --flush_redlist.")

    argp.add_argument("--flush_redlist", default=False, action="store_true",
                      help="Cleans the redlist.")



    opts = argp.parse_args()

    if opts.version:
        print("wpm v%s" % wpm.__version__)
        print(wpm.__copyright__)
        print("Source code (sans quotes) distributed under the %s" % wpm.__license__)
        sys.exit(0)
    
    if opts.flush_redlist:
        wpm.quotes.Quotes.save_redlist({})
        sys.exit(0)

    opts.stats_file = os.path.expanduser(opts.stats_file)
    return opts

def load_stats(filename, tag):
    """Loads CSV stats from file."""
    if not os.path.isfile(filename):
        return wpm.stats.Stats(tag)

    try:
        stats = wpm.stats.Stats.load(filename)
    except ValueError:
        new_name = filename + ".old"
        print("Unsupported format. Renaming %s to %s" % (filename,
                                                         new_name))
        os.rename(filename, new_name)
        stats = wpm.stats.Stats()

    if tag is not None:
        stats.tag = tag

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

def print_stats(stats, cpm):
    """Prints table of game results."""
    table = []

    config = wpm.config.Config()
    percent = config.wpm.confidence_level

    for tag in sorted(stats.games.keys()):
        name = tag if tag is not None else "n/a"

        for last_n in [0, 10, 50, 100, 500, 1000]:
            results = stats.results(tag, last_n=last_n)

            if len(results) >= last_n:
                if last_n == 0:
                    label = len(results)
                else:
                    label = "n-%d" % last_n

                avg, acc_avg = results.averages()
                sd, acc_sd = results.stddevs()

                if cpm:
                    avg = wpm_to_cpm(avg)
                    sd = wpm_to_cpm(sd)

                alpha = 1.0 - percent
                ci = confidence_interval(avg, sd, len(results), alpha)
                pi = prediction_interval(avg, sd, alpha)

                table.append([name,
                              label,
                              avg,
                              sd,
                              100.0*acc_avg,
                              100.0*acc_sd,
                              ci[0],
                              ci[1],
                              pi[0],
                              pi[1]])

    if table:
        width = max(max(len(e[0]) for e in table), 11)
    else:
        width = 0

    head0 = "Tag          Games    %s                                     Accuracy" % ("CPM" if cpm else "WPM")
    head1 = "                      avg     sd     %2d%% ci      %2d%% pi       avg     sd   " % (100*percent, 100*percent)

    if cpm:
        head0 += "            "
        head1 += "            "

    print("="*len(head1))
    print(head0)
    print(head1)
    print("-"*len(head1))

    for entry in table:
        label, count, avg, sd, acc_avg, acc_sd, ci0, ci1, pi0, pi1 = entry
        if cpm:
            print("%-*s   %6s  %7.1f  %7.1f   %7.1f-%7.1f %7.1f-%7.1f %5.1f%%  %5.1f%%" %
                  (width, label, count, avg, sd, ci0, ci1, pi0, pi1, acc_avg, acc_sd))
        else:
            print("%-*s   %6s  %5.1f  %5.1f   %5.1f-%5.1f %5.1f-%5.1f %5.1f%%  %5.1f%%" %
                  (width, label, count, avg, sd, ci0, ci1, pi0, pi1, acc_avg, acc_sd))

    print("="*len(head1))

def search(quotes, query):
    """Returns text IDs for quotes matching query."""
    for quote in iter(quotes):
        quote = wpm.quotes.Quote.from_tuple(quote)

        author = quote.author.lower()
        title = quote.title.lower()
        text = quote.text.lower()

        if (query in text) or (query in author) or (query in title):
            yield quote.text_id


def short_quotes_first(quotes, cutoff=0.2):
    """Returns text IDs of all quotes with shorter ones first (but still
    randomized)."""

    cutoff = cutoff / 0.5  # find absolute cutoff percentage based on avg (0.5)
    words = 0

    def word_length(text):
        return len(text.split(" "))

    # Find average number of words first
    for quote in iter(quotes):
        quote = wpm.quotes.Quote.from_tuple(quote)
        words += word_length(quote.text)

    avg = words / len(quotes)
    threshold = int(math.ceil(avg * cutoff))

    # Put short quotes i a randomized, starting bucket
    short = []
    for quote in iter(quotes):
        quote = wpm.quotes.Quote.from_tuple(quote)
        if word_length(quote.text) < threshold:
            short.append(quote.text_id)

    random.shuffle(short)
    return short


def main():
    """Main entry point for command line invocation."""
    try:
        opts = parse_args()

        config = wpm.config.Config()
        if config.wpm.cpm:
            opts.cpm = True

        redlist_threshold = config.wpm.redlist_threshold

        stats = load_stats(opts.stats_file, opts.tag)

        if opts.load_json is not None:
            quotes = load_json_quotes(opts.load_json)
        elif opts.load is not None:
            quotes = load_plain_text_quote([], opts.load)
        else:
            # Load default database
            quotes = wpm.quotes.Quotes.load()

        if opts.stats:
            print_stats(stats, opts.cpm)
            return

        text_ids = None

        if opts.search:
            text_ids = list(search(quotes, opts.search.lower()))

            if not text_ids:
                print("No quotes matching %r" % opts.search)
                sys.exit(1)
        elif opts.short:
            text_ids = short_quotes_first(quotes)
        elif opts.id is not None:
            text_ids = [opts.id]
    except wpm.error.WpmError as error:
        print(error)
        sys.exit(1)

    try:
        with wpm.game.GameManager(quotes, stats, opts.cpm, opts.monochrome, opts.redlist, redlist_threshold) as gm:
            try:
                gm.run(to_front=text_ids)
                gm.stats.save(opts.stats_file)
            except KeyboardInterrupt:
                gm.stats.save(opts.stats_file)
                sys.exit(0)
    except wpm.error.WpmError as error:
        print(error)
        sys.exit(1)
