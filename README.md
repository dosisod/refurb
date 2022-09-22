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

## Installing (For Development)

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

## Explainations For Checks

You can use `refurb --explain FURB123`, where `FURB123` is the error code you are trying to look up.
For example:

````
$ refurb --explain FURB123
Don't cast a variable or literal if it is already of that type. For
example:

Bad:

```
name = str("bob")
num = int(123)
```

Good:

```
name = "bob"
num = 123
````

## Ignoring Certain Checks

Use `--ignore 123` to ignore check 123. The error code can be in the form `FURB123` or `123`.

## Configuring Refurb

In addition to the command line arguments, you can also add your settings in the `pyproject.toml` file.
For example, the following command line arguments:

```
refurb file.py --ignore 100 --load some_dir
```

Corresponds to the following in your `pyproject.toml` file:

```
[tool.refurb]
ignore = [100]
load = ["some_dir"]
```

And all you need to run is `refurb file.py`!

> Note that `ignore` and `load` are the only supported options in the config file, since
> all other command line options are one-offs, and don't make sense to be in the config file.

## Writing Your Own Check

If you want to extend Refurb with your own custom checks, you can easily do so with
the `refurb gen` command. Note that this command uses the `fzf` fuzzy-finder for the
getting user input, so you will need to [install it](https://github.com/junegunn/fzf#installation)
before continuing.

This is the basic overview of creating a new check using the `refurb gen` command:

1. First select the node type you want to accept
2. Then type in the path of where you want to put your check file
3. Add your code to the generated file

> To get an idea of what you need to do to get your check working the way you want it,
> use the `--debug` flag to see the AST representation of a given file.

To run, use `refurb file.py --load your.path.here`

> Note that when using `--load`, you need to use dots in your argument, just like
> importing a normal python module.

## Plugins (Coming Soon)

Work is underway to make Refurb plugin-extensible.

## Why Does This Exist?

I love doing code reviews: I like taking something and making it better, faster, more
elegant, and so on. Lots of static analysis tools already exist, but none of them seem
to be focused on making code more elegant, more readable, more modern. That is what
Refurb tries to do.

## What Refurb Is Not

Refurb is not a linter or a type checker. It is not meant as a first-line of defense for
finding bugs, it is meant for making nice code look even better.
