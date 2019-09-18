GPG := gpg
PYFLAKES := pyflakes
PYLINT := python3 -m pylint
PYPY := pypy
PYTHON := python
PYTHON3 := python3
TWINE := python3 -m twine

default: test

test:
	$(PYTHON) setup.py test

check: test lint pylint tox

tox:
	$(PYTHON3) -m tox

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

monochrome:
	@PYTHONPATH=. $(PYTHON) wpm --monochrome

remove-prefixes:
	PYTHONPATH=. $(PYTHON) tools/remove-prefixes.py

dist:
	rm -rf dist/*
	WHEEL_TOOL=$(shell which wheel) $(PYTHON) setup.py sdist bdist_wheel

dist-sign: dist
	find dist -type f -exec $(GPG) --detach-sign -a {} \;

publish: dist-sign
	$(TWINE) upload dist/*

setup-pypi-test:
	$(PYTHON) setup.py register -r pypitest
	$(PYTHON) setup.py sdist bdist_wheel upload -r pypitest

setup-pypi-publish:
	$(PYTHON) setup.py register -r pypi
	$(PYTHON) setup.py sdist bdist_wheel upload --sign -r pypi

lint:
	$(PYFLAKES) wpm

pylint:
	$(PYLINT) --exit-zero wpm/*.py

clean:
	find . -name '*.pyc' -exec rm -f {} \;
	rm -rf wpm.egg-info .eggs build dist
