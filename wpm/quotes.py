#! /usr/bin/env python
# -*- encoding: utf-8 -*-

import codecs
import json
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

    def next(self):
        self.index = (self.index + 1) % len(self.quotes)
        if self.index == 0:
            random.shuffle(self.indices)
        return self._current()

    def previous(self):
        self.index = (self.index - 1) % len(self.quotes)
        return self._current()


class Quotes(object):
    def __init__(self, quotes=None):
        self.quotes = quotes

    def __len__(self):
        return len(self.quotes)

    def __getitem__(self, index):
        author, title, quote = self.quotes[index]
        return {"author": author, "title": title, "text": quote}

    def random_iterator(self):
        return RandomIterator(self)

    @staticmethod
    def _database_filename():
        return pkg_resources.resource_filename("wpm", "data/examples.json")

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

        with codecs.open(filename, mode="r", encoding="utf-8") as f:
            return Quotes(json.load(f))

    def save(self, filename):
        with codecs.open(filename, mode="w", encoding="utf-8") as f:
            json.dump(self.quotes, f)
