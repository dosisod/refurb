test: flake8 mypy black isort test-unit

flake8:
	flake8

mypy:
	mypy -p refurb
	mypy -p test

black:
	black refurb test -l 79 --check --diff --color

isort:
	isort . --diff --check

test-unit:
	python3 -m test.test_all
