test: flake8 mypy black isort test-unit

install:
	pip install -r requirements.txt
	pip install -r dev-requirements.txt

flake8:
	flake8

mypy:
	mypy -p refurb
	mypy -p test --exclude "test/data/*"

black:
	black refurb test -l 79 --check --diff --color --exclude "test/data/*"

isort:
	isort . --diff --check

test-unit:
	pytest

test-e2e:
	pip install -e .
	refurb test/e2e/dummy.py
