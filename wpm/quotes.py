#! /usr/bin/env python
# -*- encoding: utf-8 -*-

import codecs
import gzip
import json
import os
import pkg_resources
import random

class RandomIterator(object):
    """Random, bi-directional iterator."""
    def __init__(self, quotes):
        self.quotes = quotes
        self.indices = list(range(len(self.quotes)))
        self.index = 0
        random.shuffle(self.indices)

    def _current(self):
        i = self.indices[self.index]
        return self.quotes[i]

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
        author, title, quote = self.quotes[index]
        return {"author": author, "title": title, "text": quote}

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

        unique = set()

        for quote in quotes:
            author = quote["author"]
            title = quote["title"]
            text = quote["text"]
            unique.add((author, title, text))

        return Quotes(list(unique))

    @staticmethod
    def load(filename=None):
        if filename is None:
            filename = Quotes._database_filename()
            database = "default"
        else:
            database = os.path.splitext(os.path.basename(filename))[0]

        with gzip.open(filename) as f:
            return Quotes(json.load(f), database)

    def save(self, filename):
        with gzip.open(filename, mode="wb") as f:
            json.dump(self.quotes, f)
