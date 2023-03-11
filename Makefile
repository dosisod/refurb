.PHONY: install ruff mypy black isort test test-e2e refurb docs

all: ruff mypy black isort test refurb docs

install:
	pip install .
	pip install -r dev-requirements.txt

install-local:
	pip install -e .

ruff:
	ruff refurb test

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

test/%.txt: test/%.py
	refurb "$^" --enable-all --quiet > "$@" || true

update-tests: $(patsubst %.py,%.txt,$(wildcard test/data*/*.py))

docs:
	python3 -m docs.gen_checks
