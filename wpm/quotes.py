# -*- encoding: utf-8 -*-

"""
Code for dealing with quotes.

This file is part of the wpm software.
Copyright 2017, 2018 Christian Stigen Larsen

Distributed under the GNU Affero General Public License (AGPL) v3 or later. See
the file LICENSE.txt for the full license text. This software makes use of open
source software.

The quotes database is *not* covered by the AGPL!
"""

import codecs
import gzip
import json
import os
import random
import sys

import pkg_resources

class Quote(object):
    """Holds a single quote."""
    # pylint: disable=too-few-public-methods

    def __init__(self, author, title, text, text_id):
        self.author = author
        self.text = text
        self.title = title
        self.text_id = text_id

    @staticmethod
    def from_tuple(data):
        """Converts tuple of (author, text, title, text_id) to Quote object."""
        author = data[0]
        text = data[1]
        title = data[2]
        text_id = data[3]
        return Quote(author, title, text, text_id)

    def __str__(self):
        return "\"%s\"\n\t- %s: %s" % (self.text, self.author, self.title)


class RandomIterator(object):
    """Random, bi-directional iterator."""
    def __init__(self, quotes):
        self.quotes = quotes
        self.indices = list(range(len(self.quotes)))
        self.index = 0
        random.shuffle(self.indices)

    def __len__(self):
        return len(self.quotes)

    def current(self):
        """Returns current quote."""
        index = self.indices[self.index]
        return self._get_quote(index)

    def __getitem__(self, index):
        return self._get_quote(index)

    def _get_quote(self, index):
        quote = self.quotes[index]
        author = quote[0]
        title = quote[1]
        text = quote[2]
        if len(quote) > 3:
            text_id = quote[3]
        else:
            text_id = index
        return Quote(author, title, text, text_id)

    def put_to_front(self, text_ids):
        """Puts given text IDs to the very front of the queue."""
        front = []
        back = []

        for index in range(len(self.quotes)):
            quote = self[index]

            if quote.text_id in text_ids:
                front.append(index)
            else:
                back.append(index)

        random.shuffle(back)
        self.indices = front + back
        self.index = 0

    @property
    def database(self):
        """The quotes database."""
        return self.quotes.database

    @property
    def text_id(self):
        """Returns text ID of current quote."""
        return self.indices[self.index]

    def next(self):
        """Goes to next quote."""
        self.index = (self.index + 1) % len(self.quotes)
        return self.current()

    def previous(self):
        """Goes back to previous quote."""
        self.index = (self.index - 1) % len(self.quotes)
        return self.current()


class Quotes(object):
    """Container for quotes."""
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
        """Returns a random iterator for all the quotes."""
        return RandomIterator(self)

    @staticmethod
    def _database_filename():
        """Returns the filename of the packaged database."""
        return pkg_resources.resource_filename("wpm", "data/examples.json.gz")

    @staticmethod
    def load_json(filename=None):
        """Loads quotes from a JSON file."""
        if filename is None:
            filename = Quotes._database_filename()

        with codecs.open(filename, encoding="utf-8") as file_obj:
            quotes = json.load(file_obj)

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
        """Loads quotes from gzipped JSON file."""
        if filename is None:
            filename = Quotes._database_filename()
            database = "default"
        else:
            database = os.path.splitext(os.path.basename(filename))[0]

        args = {"filename": filename, "mode": "rt"}
        if sys.version_info.major == 3:
            args["encoding"] = "utf-8"

        with gzip.open(**args) as file_obj:
            quotes = json.load(file_obj)
            quotes = tuple(map(tuple, quotes))
            return Quotes(quotes, database)

    def save(self, filename=None):
        """Saves current quotes to gzipped JSON file."""
        if filename is None:
            filename = Quotes._database_filename()

        args = {"filename": filename, "mode": "wt"}
        if sys.version_info.major == 3:
            args["encoding"] = "utf-8"

        with gzip.open(**args) as file_obj:
            json.dump(self.quotes, file_obj)
