import csv

from wpm.difficulty import Difficulty
from wpm.quotes import Quotes
from wpm.stats import Stats

if __name__ == "__main__":
    print("Loading databases")
    stats = Stats.load()
    quotes = Quotes.load()
    results = list(stats.results().results)
    diffs = Difficulty.load()

    print("Dumping CSV file with (wpm, accuracy, difficulty, length)")

    rows = [(r.wpm, r.accuracy,
             diffs[r.text_id],
             len(quotes.from_id(r.text_id).text),
            ) for r in results]

    with open("diffs.csv", "wb") as csvfile:
        csvw = csv.writer(csvfile)
        for row in rows:
            csvw.writerow(row)
