.PHONY: install flake8 mypy black isort test test-e2e refurb

all: flake8 mypy black isort test refurb

install:
	pip install .
	pip install -r dev-requirements.txt

install-local:
	pip install -e .

flake8:
	flake8

mypy:
	mypy refurb
	mypy test --exclude "test/data*"

black:
	black refurb test

isort:
	isort . --diff --check

test:
	pytest

test-e2e: install-local
	refurb test/e2e/dummy.py

refurb:
	refurb refurb test/*.py

test/data/%.txt: test/data/%.py
	refurb "$^" --enable-all --quiet > "$@" || true

update-tests: $(patsubst %.py,%.txt,$(wildcard test/data/*.py))
