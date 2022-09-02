# Refurb

A tool for refurbishing and modernizing Python codebases.

## Example

```python
# main.py

with open("file.txt") as f:
    contents = f.read()
```

Running:

```
$ refurb main.py
tmp.py:3:1 [FURB101]: Use `y = Path(x).read_text()` instead of `with open(x, ...) as f: y = f.read()`
```

## Installing

Before installing, it is recommended that you setup a [virtual environment](https://docs.python.org/3/tutorial/venv.html).

```
$ pip3 install refurb
$ refurb file.py
```

## Installing (for development)

```
$ git clone https://github.com/dosisod/refurb
$ cd refurb
$ make install
$ make install-local
```

Tests can be ran all at once with `make`, or you can run each tool on its own using
`make black`, `make flake8`, and so on.

Unit tests can be ran with `pytest` or `make test`.

> Since the end-to-end (e2e) tests are slow, they are not ran when running `make test`.
> You will need to run `make test-e2e` to run them.

## Why does this exist?

I love doing code reviews: I like taking something and making it better, faster, more
elegant, and so on. Lots of static analysis tools already exist, but none of them seem
to be focused on making code more elegant, more readable, more modern. That is what
Refurb tries to do.

## What Refurb IS NOT

Refurb is not a linter or a type checker. It is not meant as a first-line of defense for
finding bugs, it is meant for making nice code look even better.
