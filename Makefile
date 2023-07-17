.PHONY: install ruff mypy black isort test test-e2e refurb docs

all: ruff mypy black isort test refurb docs

install:
	poetry install

ruff:
	poetry run ruff refurb test

mypy:
	poetry run mypy refurb test --exclude 'test.data*'

black:
	poetry run black refurb test

isort:
	poetry run isort . --diff --check

test:
	poetry run pytest

test-e2e: install
	poetry run refurb test/e2e/dummy.py

refurb:
	poetry run refurb refurb test/*.py

test/%.txt: test/%.py
	poetry run refurb "$^" --enable-all --quiet > "$@" || true

update-tests: $(patsubst %.py,%.txt,$(wildcard test/data*/*.py))

docs:
	poetry run python3 -m docs.gen_checks
