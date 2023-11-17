# Categories

Here is a list of the built-in categories in Refurb, and their meanings.

## `abc`

These check for code relating to [Abstract Base Classes](https://docs.python.org/3/library/abc.html).

## `builtin`

Checks that have the `builtin` category cover a few different topics:

* Built-in functions such as `print()`, `open()`, `str()`, and so on
* Statements such as `del`
* File system related operations such as `open()` and `readlines()`

## `control-flow`

These checks deal with the control flow of a program, such as optimizing usage
of `return` and `continue`, removing `if` statements under certain conditions,
and so on.

## `contextlib`

These checks are for the [contextlib](https://docs.python.org/3/library/contextlib.html)
standard library module.

## `datetime`

These checks are for the [datetime](https://docs.python.org/3/library/datetime.html)
standard library module.

## `decimal`

These checks are for the [decimal](https://docs.python.org/3/library/decimal.html)
standard library module.

## `dict`

These checks cover:

* Usage of `dict` objects
* In some cases, objects supporting the [Mapping](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping) protocol

## `fastapi`

These are checks relating to the third-party [FastAPI](https://github.com/tiangolo/fastapi) library.

## `fstring`

These checks relate to Python's [f-strings](https://fstring.help/).

## `fractions`

These checks are for the [fractions](https://docs.python.org/3/library/fractions.html)
standard library module.

## `functools`

These checks relate to the [functools](https://docs.python.org/3/library/functools.html)
standard library module.

## `hashlib`

These checks relate to the [hashlib](https://docs.python.org/3/library/hashlib.html)
standard library module.

## `iterable`

These checks cover:

* Iterable types such as `list` and `tuple`
* Standard library objects which are commonly iterated over such as `dict` keys

## `itertools`

These checks relate to the [itertools](https://docs.python.org/3/library/itertools.html)
standard library module.

## `math`

These checks relate to the [math](https://docs.python.org/3/library/math.html)
standard library module.

## `operator`

These checks relate to the [operator](https://docs.python.org/3/library/operator.html)
standard library module.

## `logical`

These checks relate to logical cleanups and optimizations, primarily in `if` statements,
but also in boolean expressions.

## `list`

These checks cover usage of the built-in `list` object.

## `pattern-matching`

Checks related to Python 3.10's [Structural Pattern Matching](https://peps.python.org/pep-0636/).

## `pathlib`

These checks relate to the [pathlib](https://docs.python.org/3/library/pathlib.html)
standard library module.

## `performance`

These checks are supposted to find slow code that can be written faster. The threshold for
"fast" and "slow" are somewhat arbitrary and depend on the check, but in general you should
expect that a check in the `performance` category will make your code faster (and should never
make it slower).

## `python39`, `python310`, `python311`

These checks are only enabled for Python versions 3.9, 3.10, or 3.11 respectively, or in some
way are improved in later versions of Python. For example, `isinstance(x, y) or isinstance(x, z)`
can be written as `isinstance(x, (y, z))` in any Python version, but in Python 3.10+ it can
be written as `isinstance(x, y | z)`.

## `pythonic`

This is a general catch-all for things which are "unpythonic". It differs from the
`readability` category because "unreadable" code can still be pythonic.

## `readability`

These checks aim to make existing code more readable. This can be subjective, but in general,
they reduce the horizontal or vertical length of your code, or make the underlying meaning
of the code more apparent.

## `regex`

These checks are for the [`re`](https://docs.python.org/3/library/contextlib.html) standard library module.

## `scoping`

These checks have to do with Python's scoping rules. For more info on how Python's scoping
rules work, read [this article](https://realpython.com/python-scope-legb-rule/).

## `secrets`

These checks are for the [secrets](https://docs.python.org/3/library/secrets.html)
standard library module.

## `set`

These checks deal with usage of [`set`](https://docs.python.org/3/tutorial/datastructures.html#sets)
objects in Python.

## `shlex`

These checks are for the [shlex](https://docs.python.org/3/library/shlex.html)
standard library module.

## `string`

These checks deal with usage of [`str`](https://docs.python.org/3/library/stdtypes.html#string-methods)
objects in Python.

## `truthy`

These checks cover truthy and falsy operations in Python, primarily in the context of `assert` and `if`
statements.
