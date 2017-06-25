import argparse
import codecs
import pkg_resources
import random
import sys
import urwid
import wpm

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

    opts = p.parse_args()

    if opts.version:
        print("WPM v%s" % wpm.__version__)
        print(wpm.__copyright__)
        print("Distributed under the %s" % wpm.__license__)
        sys.exit(0)

    return opts

def main():
    opts = parse_args()
    texts = []

    if opts.load_json is not None:
        texts += wpm.load(opts.load_json)

    if opts.load is not None:
        with codecs.open(opts.load, encoding="utf-8") as f:
            texts.append({"author": "", "title": "", "text": f.read()})

    if len(texts) == 0:
        filename = pkg_resources.resource_filename("wpm", "data/examples.json")
        texts = wpm.load(filename)

    try:
        game = wpm.GameRound(random.choice(texts))
        game.run()
    except urwid.main_loop.ExitMainLoop:
        pass
