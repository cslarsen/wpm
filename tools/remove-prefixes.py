import wpm.quotes

quotes = wpm.quotes.Quotes.load()

for i, quote in enumerate(quotes):
    author, title, text = quote
    prefixes = (
        "a",
        "book",
        "by",
        "directed",
        "movie",
        "other",
        "song",
        "speech",
        "television series",
    )
    while author.lower().split(" ")[0] in prefixes:
        author = " ".join(author.split(" ")[1:])
    if author != quote[0]:
        print(quote[0], author)
        quotes[i] = [author, title, text]

quotes.save()
