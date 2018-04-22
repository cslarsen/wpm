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

profile:
	PYTHONPATH=. $(PYTHON) -m cProfile -o stats wpm/__main__.py
	python -c 'import pstats; p = pstats.Stats("stats"); p.sort_stats("cumulative").print_stats(10)'

help:
	PYTHONPATH=. $(PYTHON) wpm --help

run3:
	PYTHONPATH=. $(PYTHON3) wpm

runpypy:
	PYTHONPATH=. $(PYPY) wpm

stats:
	PYTHONPATH=. $(PYTHON) wpm --stats

remove-prefixes:
	PYTHONPATH=. $(PYTHON) tools/remove-prefixes.py

dist:
	rm -rf dist/*
	WHEEL_TOOL=$(shell which wheel) $(PYTHON) setup.py sdist

publish: dist
	find dist -type f -exec gpg2 --detach-sign -a {} \;
	twine upload dist/*

setup-pypi-test:
	$(PYTHON) setup.py register -r pypitest
	$(PYTHON) setup.py sdist upload -r pypitest

setup-pypi-publish:
	$(PYTHON) setup.py register -r pypi
	$(PYTHON) setup.py sdist upload --sign -r pypi

lint:
	@$(PYFLAKES) `find . -name '*.py' -print`

pylint:
	@$(PYLINT) wpm/*.py

clean:
	find . -name '*.pyc' -exec rm -f {} \;
	rm -rf wpm.egg-info .eggs build dist
