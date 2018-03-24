#! /usr/bin/env python
# -*- encoding: utf-8 -*-

import codecs
import gzip
import json
import os
import pkg_resources
import random

class Quote(object):
    def __init__(self, author, title, text, text_id):
        self.author = author
        self.text = text
        self.title = title
        self.text_id = text_id


class RandomIterator(object):
    """Random, bi-directional iterator."""
    def __init__(self, quotes):
        self.quotes = quotes
        self.indices = list(range(len(self.quotes)))
        self.index = 0
        random.shuffle(self.indices)

    def __len__(self):
        return len(self.quotes)

    def _current(self):
        index = self.indices[self.index]

        quote = self.quotes[index]
        author = quote[0]
        title = quote[1]
        text = quote[2]

        if len(quote) > 3:
            text_id = quote[3]
        else:
            text_id = index

        return Quote(author, title, text, text_id)

    @property
    def database(self):
        return self.quotes.database

    @property
    def text_id(self):
        return self.indices[self.index]

    def next(self):
        self.index = (self.index + 1) % len(self.quotes)
        if self.index == 0:
            random.shuffle(self.indices)
        return self._current()

    def previous(self):
        self.index = (self.index - 1) % len(self.quotes)
        return self._current()


class Quotes(object):
    def __init__(self, quotes=None, database=None):
        self.quotes = quotes
        self.database = database

    def __len__(self):
        return len(self.quotes)

    def __getitem__(self, index):
        return self.quotes[index]

    def __setitem__(self, index, item):
        if not isinstance(item, list):
            raise ValueError("Expected a list")
        if len(item) != 3:
            raise ValueError("Expected a list of three strings")
        self.quotes[index] = item

    def random_iterator(self):
        return RandomIterator(self)

    @staticmethod
    def _database_filename():
        return pkg_resources.resource_filename("wpm", "data/examples.json.gz")

    @staticmethod
    def load_json(filename=None):
        if filename is None:
            filename = Quotes._database_filename()

        with codecs.open(filename, encoding="utf-8") as f:
            quotes = json.load(f)

        # Flatten
        out = []
        for text_id, quote in enumerate(quotes):
            author = quote["author"]
            title = quote["title"]
            text = quote["text"]
            text_id = int(quote.get("id", text_id))
            out.append((author, title, text, text_id))

        return Quotes(list(set(out)))

    @staticmethod
    def load(filename=None):
        if filename is None:
            filename = Quotes._database_filename()
            database = "default"
        else:
            database = os.path.splitext(os.path.basename(filename))[0]

        with gzip.open(filename) as f:
            quotes = json.load(f)
            quotes = tuple(map(tuple, quotes))
            return Quotes(quotes, database)

    def save(self, filename=None):
        if filename is None:
            filename = Quotes._database_filename()

        with gzip.open(filename, mode="wb") as f:
            json.dump(self.quotes, f)
