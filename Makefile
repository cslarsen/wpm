PYTHON := python
PYPY := pypy
PYTHON3 := python3
PYFLAKES := pyflakes
PYLINT := pylint

default: test

test:
	$(PYTHON) setup.py test

check: test

run:
	PYTHONPATH=. $(PYTHON) wpm

repl:
	PYTHONPATH=. $(PYTHON) -i -c \
		'from wpm.stats import*; from wpm.quotes import *; from wpm.difficulty import *; quotes = Quotes.load(); stats = Stats.load(); diffs = Difficulty.load()'

profile:
	PYTHONPATH=. $(PYTHON) -m cProfile -o stats wpm/__main__.py
	python -c 'import pstats; p = pstats.Stats("stats"); p.sort_stats("cumulative").print_stats(10)'

help:
	PYTHONPATH=. $(PYTHON) wpm --help

dump:
	PYTHONPATH=. $(PYTHON) tools/dumpdiffs.py

run3:
	PYTHONPATH=. $(PYTHON3) wpm

runpypy:
	PYTHONPATH=. $(PYPY) wpm

stats:
	@PYTHONPATH=. $(PYTHON) wpm --stats

remove-prefixes:
	PYTHONPATH=. $(PYTHON) tools/remove-prefixes.py

dist:
	rm -rf dist/*
	WHEEL_TOOL=$(shell which wheel) $(PYTHON) setup.py bdist_wheel

publish: dist
	find dist -type f -exec gpg2 --detach-sign -a {} \;
	twine upload dist/*

setup-pypi-test:
	$(PYTHON) setup.py register -r pypitest
	$(PYTHON) setup.py bdist_wheel upload -r pypitest

setup-pypi-publish:
	$(PYTHON) setup.py register -r pypi
	$(PYTHON) setup.py bdist_wheel upload --sign -r pypi

lint:
	@$(PYFLAKES) `find . -name '*.py' -print`

pylint:
	@$(PYLINT) wpm/*.py

clean:
	find . -name '*.pyc' -exec rm -f {} \;
	rm -rf wpm.egg-info .eggs build dist
