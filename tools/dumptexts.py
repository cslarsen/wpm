#! /usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Dumps texts from typeracerdata.com.
"""

import hashlib
import os
import json
import urllib2
from HTMLParser import HTMLParser

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
        author = author[1:]
    author = author.strip()

    prefixes = (
        "a book",
        "a movie",
        "a song",
        "a speech",
        "a television series",
        "by",
    )
    for p in prefixes:
        if author.lower().startswith(p.lower()):
            author = author[len(p):].strip()

    author = normalize(author)
    title = normalize(title)
    quote = normalize(quote)

    return author, title, quote

def main(verbose=False):
    print("Reading main list of quotes")
    html = loadurl("http://www.typeracerdata.com/texts")

    ids = set()
    for line in html.split("\n"):
        find = "/text?id="
        if not find in line:
            continue
        start = line.index(find)
        stop = line.index('"', start + len(find))
        text_id = line[start + len(find):stop]
        ids.add(text_id)

    print("Found %d quotes" % len(ids))

    # TODO: Do in parallel
    quotes = []
    try:
        for num, text_id in enumerate(ids):
            html = get_text(text_id)
            author, title, quote = process(text_id, html)
            quotes.append({
                "author": author,
                "title": title,
                "text": quote,
            })
            print("** count %d id %s" % (num, text_id))
            if verbose:
                print("\"%s\" by %s" % (title, author))
                print("\"%s\"" % quote)
                print("")
    except KeyboardInterrupt:
        pass
    print("Saving quotes.json")

    with open("../wpm/data/examples.json", "rt") as f:
        examples = json.load(f)

    oldcount = len(examples)

    # Make quotes unique
    unique = set()
    for quote in examples + quotes:
        author = quote["author"]
        title = quote["title"]
        text = quote["text"]
        unique.add((author, title, text))

    examples = []
    for author, title, text in unique:
        examples.append({
            "author": author,
            "title": title,
            "text": text,
        })

    with open("../wpm/data/examples.json", "wt") as f:
        json.dump(examples, f)

    print("Total quote count in database: %d" % len(examples))

if __name__ == "__main__":
    main()
