import os
import unittest

from wpm.error import WpmError
from wpm.quotes import Quotes, Quote


class QuotesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.quotes = Quotes.load()

    def test_default_database(self):
        self.assertGreaterEqual(len(self.quotes), 4000)

    def test_from_id(self):
        with self.assertRaises(KeyError):
            self.quotes.from_id(-1)

        text_id = 3621031
        quote = self.quotes.from_id(text_id)
        self.assertEqual(quote.text_id, text_id)
        self.assertEqual(quote.author, "Joseph Heller")
        self.assertEqual(quote.title, "Catch-22")
        self.assertTrue(quote.text.startswith("Let's take a drive"))

    def test_load_json(self):
        filename = os.path.join(os.path.dirname(__file__), "test.json")

        quotes = Quotes.load_json(filename)
        self.assertEqual(len(quotes), 1)

        quote = quotes.at(0)
        self.assertEqual(quote.author, "Mr. Author")
        self.assertEqual(quote.title, "The Title")
        self.assertEqual(quote.text, "This is the text.")

    def test_load_json_missing_file(self):
        with self.assertRaises(WpmError):
            Quotes.load_json("non-existing-file")

    def test_load_json_invalid_format(self):
        with self.assertRaises(WpmError):
            Quotes.load_json(__file__)


class QuoteTests(unittest.TestCase):
    def test_from_tuple(self):
        author = "The Author"
        title = "The Title"
        text = "The Text."
        text_id = 123

        quote = Quote.from_tuple((author, title, text, text_id))

        self.assertEqual(quote.author, author)
        self.assertEqual(quote.title, title)
        self.assertEqual(quote.text, text)
        self.assertEqual(quote.text_id, text_id)
