PYTHON := python
PYTHON3 := python3.6
PYFLAKES := pyflakes

default: test

test:
	$(PYTHON) setup.py test

check: test

run:
	PYTHONPATH=. $(PYTHON) wpm

run3:
	PYTHONPATH=. $(PYTHON3) wpm

stats:
	PYTHONPATH=. $(PYTHON) wpm --stats

dist:
	rm -rf dist/*
	WHEEL_TOOL=$(shell which wheel) $(PYTHON) setup.py sdist

count:
	@grep '"author"' wpm/data/examples.json | wc -l

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
	@(json_pp < wpm/data/examples.json >/dev/null) || echo bad json && echo json ok

clean:
	find . -name '*.pyc' -exec rm -f {} \;
	rm -rf wpm.egg-info .eggs build dist
