.PHONY: install ruff mypy black isort typos test test-e2e refurb docs

all: ruff mypy black isort typos test refurb docs

install:
	pip install -e .
	pip install -r dev-requirements.txt

ruff:
	ruff refurb test

mypy:
	mypy refurb
	mypy test --exclude "test/data*"

black:
	black refurb test --check --diff

isort:
	isort . --diff --check

typos:
	typos --format brief

test:
	pytest

test-e2e: install
	refurb test/e2e/dummy.py

refurb:
	refurb refurb test/*.py

test/%.txt: test/%.py
	refurb "$^" --enable-all --quiet --no-color > "$@" || true

update-tests: $(patsubst %.py,%.txt,$(wildcard test/data*/*.py))

docs:
	python3 -m docs.gen_checks

fmt:
	ruff refurb test --fix
	isort .
	black refurb test

clean:
	rm -rf .mypy_cache .ruff_cache .pytest_cache
