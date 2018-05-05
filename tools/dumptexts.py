#! /usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Dumps texts from typeracerdata.com.
"""

from HTMLParser import HTMLParser
from multiprocessing import Pool as ThreadPool
import argparse
import gzip
import hashlib
import json
import os
import pickle
import urllib2

def normalize(s):
    # Unescape html
    s = s.decode("utf-8")
    s = HTMLParser().unescape(s)
    s = s.replace("\n", " ")
    s = s.replace("\r", " ")

    while "  " in s:
        s = s.replace("  ", " ")

    return s.strip()

def loadurl(url):
    cache = os.path.join("cache", hashlib.sha1(url).hexdigest())
    if os.path.isfile(cache):
        with open(cache, "rt") as f:
            return f.read()

    html = urllib2.urlopen(url).read()

    with open(cache, "wt") as f:
        f.write(html)

    return html

def get_texts():
    return loadurl("http://www.typeracerdata.com/texts")

def get_text(text_id):
    url = "http://typeracerdata.com/text?id=%s" % text_id
    html = loadurl(url)
    return html

def process(text_id, html):
    """
<h1>Text #3550073</h1>

<p>
 Plato is always concerned to advocate views that will make people what he
 thinks virtuous; he is hardly ever intellectually honest, because he allows
 himself to judge doctrines by their social consequences.</p>

<p>- from <em>The History of Western Philosophy</em>, a book Bertrand
Russel</p>
    """
    def skip(s, tag):
        pos = s.index(tag)
        assert(pos >= 0)
        return s[pos + len(tag):]

    def extract(s, tag):
        pos = s.index(tag)
        assert(pos >= 0)
        return s[:pos]

    html = skip(skip(html, "</h1>"), "<p>")
    quote = extract(html, "</p>").strip()

    html = skip(html, "<em>")
    title = extract(html, "</em>").strip()
    html = skip(html, "</em>")

    author = extract(html, "</p>").strip()
    while author[0] in ", ":
        author = author[1:].strip()

    prefixes = (
        "a",
        "book",
        "by",
        "directed",
        "movie",
        "other",
        "song",
        "speech",
        "television series",
    )
    while author.lower().split(" ")[0] in prefixes:
        author = " ".join(author.split(" ")[1:])

    author = normalize(author)
    title = normalize(title)
    quote = normalize(quote)

    return author, title, quote

def readquote(text_id):
        html = get_text(text_id)
        author, title, quote = process(text_id, html)

        print("id %s: '%s' by %s" % (text_id, title, author))
        print("   \"%s\"" % quote)

        return author, title, quote, text_id

def read_ids(url="http://www.typeracerdata.com/texts"):
    html = loadurl(url)

    ids = set()
    for line in html.split("\n"):
        find = "/text?id="
        if not find in line:
            continue
        start = line.index(find)
        stop = line.index('"', start + len(find))
        text_id = int(line[start + len(find):stop])
        ids.add(text_id)

    return ids

def make_tuple(quotes):
    return tuple(set(map(tuple, quotes)))

def get_difficulty(verbose=False):
    print("Reading list of quote scores")

    html = loadurl("http://www.typeracerdata.com/texts?sort=relative_average")

    scores = {}
    text_id = None
    score = None

    for line in html.split("\n"):
        if text_id is None:
            find = "/text?id="
            if find in line:
                start = line.index(find)
                stop = line.index('"', start + len(find))
                text_id = int(line[start + len(find):stop])
            continue
        elif score is None:
            # Find difficulty rating
            find = "<td class=\"sort\">"
            if find in line:
                start = line.index(find) + len(find)
                stop = line.index("</td>", start)
                score = float(line[start:stop])
        else:
            if score > 0:
                scores[text_id] = score
            text_id = None
            score = None

    filename = "scores.pickle"
    print("Pickling %d scores to %s" % (len(scores), filename))

    with open(filename, "wb") as file_obj:
        pickle.dump(scores, file_obj)

    return scores

def get_texts(verbose=False, threads=1):
    print("Reading list of quotes")
    ids = read_ids()

    print("Found %d quotes" % len(ids))
    print("Downloading each quote w/%d threads" % threads)

    if threads > 1:
        pool = ThreadPool(threads)
        results = pool.map(readquote, ids)
        pool.close()
        pool.join()
    else:
        try:
            results = []
            for count, text_id in enumerate(ids):
                print("%d/%d" % (count, len(ids)))
                results.append(readquote(text_id))
        except KeyboardInterrupt:
            pass

    print("Adding %d quotes to database" % len(results))

    quotes = []
    examples = []
    for author, title, quote, text_id in results:
        quotes.append([author, title, quote, text_id])

    filename = "../wpm/data/examples.json.gz"

    try:
        with gzip.open(filename) as f:
            examples = json.load(f)
    except Exception as e:
        print("Could not load %s: %s" % (filename, e))

    quotes = make_tuple(examples + quotes)

    with gzip.open(filename, mode="wb") as f:
        json.dump(quotes, f)

    print("Total quote count in database: %d" % len(quotes))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-j", "--jobs", default=1, type=int,
            help="Number of concurrent downloads")
    p.add_argument("-v", "--verbose", default=False,
            action="store_true")
    p.add_argument("--difficulty", default=False, action="store_true",
            help="Only retrieve text_id and difficulty rating")

    opts = p.parse_args()

    if opts.difficulty:
        get_difficulty(opts.verbose)
    else:
        get_texts(opts.verbose, opts.jobs)
