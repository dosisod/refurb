# Refurb

A tool for refurbishing and modernizing Python codebases.

## Example

```python
# main.py

for filename in ["file1.txt", "file2.txt"]:
    with open(filename) as f:
        contents = f.read()

    lines = contents.splitlines()

    for line in lines:
        if not line or line.startswith("# ") or line.startswith("// "):
            continue

        for word in line.split():
            print(f"[{word}]", end="")

        print("")
```

Running:

```
$ refurb main.py
main.py:3:17 [FURB109]: Use `in (x, y, z)` instead of `in [x, y, z]`
main.py:4:5 [FURB101]: Use `y = Path(x).read_text()` instead of `with open(x, ...) as f: y = f.read()`
main.py:10:40 [FURB102]: Replace `x.startswith(y) or x.startswith(z)` with `x.startswith((y, z))`
main.py:16:9 [FURB105]: Use `print() instead of `print("")`
```

## Installing

Before installing, it is recommended that you setup a [virtual environment](https://docs.python.org/3/tutorial/venv.html).

```
$ pip3 install refurb
$ refurb file.py folder/
```

> Note: Refurb only supports Python 3.10. It can check Python 3.6 code and up, but Refurb
> itself must be ran through Python 3.10.

## Explanations For Checks

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
```
````

## Ignoring Errors

Use `--ignore 123` to ignore error 123. The error code can be in the form `FURB123` or `123`.
This flag can be repeated.

> The `FURB` prefix indicates that this is a built-in error. The `FURB` prefix is optional,
> but for all other errors (ie, `ABC123`), the prefix is required.

You can also use inline comments to disable errors:

```
x = int(0)  # noqa: FURB123
y = list()  # noqa
```

Here, `noqa: FURB123` specifically ignores the FURB123 error for that line, and `noqa` ignores
all errors on that line.

## Enabling Checks

Certain checks are disabled by default, and need to be enabled first. You can do this using the
`--enable ERR` flag, where `ERR` is the error code of the check you want to enable. A disabled
check differs from an ignored check in that a disabled check will never be loaded, whereas an
ignored check will be loaded, an error will be emitted, and the error will be suppressed.

## Configuring Refurb

In addition to the command line arguments, you can also add your settings in the `pyproject.toml` file.
For example, the following command line arguments:

```
refurb file.py --ignore 100 --load some_module --quiet
```

Corresponds to the following in your `pyproject.toml` file:

```toml
[tool.refurb]
ignore = [100]
load = ["some_module"]
quiet = true
```

Now all you need to type is `refurb file.py`! Supplying command line arguments will
override any existing settings in the config file.

## Using Refurb With `pre-commit`

You can use Refurb with [pre-commit](https://pre-commit.com/) by adding the following
to your `.pre-commit-config.yaml` file:

```yaml
  - repo: https://github.com/dosisod/refurb
    rev: REVISION
    hooks:
      - id: refurb
```

Replacing `REVISION` with a version or SHA of your choosing (or leave it blank to
let `pre-commit` find the most recent one for you).

## Plugins

Installing plugins for Refurb is very easy:

```
$ pip3 install refurb-plugin-example
```

Where `refurb-plugin-example` is the name of the plugin. Refurb will automatically load
any installed plugins.

To make your own Refurb plugin, see the [`refurb-plugin-example` repository](https://github.com/dosisod/refurb-plugin-example)
for more info.

## Writing Your Own Check

If you want to extend Refurb but don't want to make a full-fledged plugin,
you can easily create a one-off check file with the `refurb gen` command.

> Note that this command uses the `fzf` fuzzy-finder for getting user input,
> so you will need to [install fzf](https://github.com/junegunn/fzf#installation) before continuing.

Here is the basic overview for creating a new check using the `refurb gen` command:

1. First select the node type you want to accept
2. Then type in where you want to save the auto generated file
3. Add your code to the new file

To get an idea of what you need to add to your check, use the `--debug` flag to see the
AST representation for a given file (ie, `refurb --debug file.py`). Take a look at the
files in the `refurb/checks/` folder for some examples.

Then, to load your new check, use `refurb file.py --load your.path.here`

> Note that when using `--load`, you need to use dots in your argument, just like
> importing a normal python module.

## Developing

To setup locally, run:

```
$ git clone https://github.com/dosisod/refurb
$ cd refurb
$ make install
$ make install-local
```

Tests can be ran all at once using `make`, or you can run each tool on its own using
`make black`, `make flake8`, and so on.

Unit tests can be ran with `pytest` or `make test`.

> Since the end-to-end (e2e) tests are slow, they are not ran when running `make`.
> You will need to run `make test-e2e` to run them.

## Why Does This Exist?

I love doing code reviews: I like taking something and making it better, faster, more
elegant, and so on. Lots of static analysis tools already exist, but none of them seem
to be focused on making code more elegant, more readable, or more modern. That is where
Refurb comes in.

Refurb is heavily inspired by [clippy](https://rust-lang.github.io/rust-clippy/master/index.html),
the built-in linter for Rust.

## What Refurb Is Not

Refurb is not a style/type checker. It is not meant as a first-line of defense for
linting and finding bugs, it is meant for making good code even better.
