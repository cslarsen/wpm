import csv

from wpm.difficulty import Difficulty
from wpm.quotes import Quotes
from wpm.stats import Stats

if __name__ == "__main__":
    print("Loading scores and difficulty scores")
    stats = Stats.load()
    results = list(stats.results().results)
    diffs = Difficulty.load()

    print("Dumping CSV file with (wpm, accuracy, difficulty)")

    with open("diffs.csv", "wb") as csvfile:
        csvw = csv.writer(csvfile)
        rows = [(r.wpm, r.accuracy, diffs[r.text_id]) for r in results]
        for row in rows:
            csvw.writerow(row)
