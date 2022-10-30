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
	mypy -p refurb
	mypy -p test --exclude "test/data*"

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
