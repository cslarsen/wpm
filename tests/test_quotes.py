import os
import unittest

import wpm.quotes

class QuotesTests(unittest.TestCase):
    def test_load_json(self):
        filename = os.path.join(os.path.dirname(__file__), "test.json")
        quotes = wpm.quotes.Quotes.load_json(filename)
        self.assertIsInstance(quotes, wpm.quotes.Quotes)
        self.assertEqual(len(quotes), 1)
        quote = quotes.at(0)
        self.assertEqual(quote.author, "Mr. Author")
        self.assertEqual(quote.title, "The Title")
        self.assertEqual(quote.text, "This is the text.")
