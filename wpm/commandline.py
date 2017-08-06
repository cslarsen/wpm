import argparse
import codecs
import os
import pkg_resources
import sys
import urwid
import wpm
import wpm.game
import wpm.stats
import wpm.addExamples

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

    p.add_argument("--tab", default=None, type=int,
            help="If set, expand tabs to this number of spaces")

    p.add_argument("--keyboard", default=None, type=str,
            help="If set, saves statistics for current keyboard")

    p.add_argument("--stats", default=False, action="store_true",
            help="Shows keyboard statistics")

    opts = p.parse_args()

    if opts.version:
        print("WPM v%s" % wpm.__version__)
        print(wpm.__copyright__)
        print("Distributed under the %s" % wpm.__license__)
        sys.exit(0)

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
    import wpm.stats

    opts = parse_args()
    texts = []

    if opts.addtext is True:
        wpm.addExamples.main()
        sys.exit(0)

    stats_file = os.path.expanduser("~/.wpm")

    if not os.path.exists(stats_file):
        stats = wpm.stats.Stats(opts.keyboard)
    else:
        stats = wpm.stats.Stats.load(stats_file)

    if opts.stats:
        for keyboard in sorted(stats.games.keys()):
            print("Keyboard: %s" % keyboard)

            games = stats.games[keyboard]
            awpm, aacc = averages(games)
            print("   all %4d games: %5.1f average wpm, %4.1f%% average accuracy" % (
                len(games), awpm, 100.0*aacc))

            last_n = 10
            if len(games) >= last_n:
                awpm, aacc = averages(games[-last_n:])
                print("  last %4d games: %5.1f average wpm, %4.1f%% average accuracy" % (
                    last_n, awpm, 100.0*aacc))
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
        stats = wpm.stats.Stats(opts.keyboard)
        game = wpm.game.Game(texts, stats)
        game.set_tab_spaces(opts.tab)
        game.run()
    except urwid.main_loop.ExitMainLoop:
        stats.save(stats_file)
