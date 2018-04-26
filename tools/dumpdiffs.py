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

    rows = []
    for r in results:
        if r.text_id not in diffs:
            continue
        diff = diffs[r.text_id]
        quote = quotes.from_id(r.text_id).text
        rows.append((r.wpm, r.accuracy, diff, len(quote)))

    with open("diffs.csv", "wb") as csvfile:
        csvw = csv.writer(csvfile)
        for row in rows:
            csvw.writerow(row)
