# Refurb

A tool for refurbish and modernize Python codebases.

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

## Why?

I love doing code reviews: I like taking something and making it better, faster, more
elegant, and so on. Lots of static analysis tools already exist, but none of them seem
to be focused on making code more elegant, more readable, more modern. That is what
Refurb tries to do.

## What Refurb IS NOT

Refurb is not a linter or a type checker. It is not meant as a first-line of defense for
finding bugs, it is meant for making nice code look even better.
