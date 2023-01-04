# Categories

Here is a list of the built-in categories in Refurb, and their meanings.

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

## `dict`

These checks cover:

* Usage of `dict` objects
* In some cases, objects supporting the [Mapping](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping) protocol

## `fstring`

These checks relate to Python's [f-strings](https://fstring.help/).

## `functools`

These checks relate to the [functools](https://docs.python.org/3/library/functools.html)
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

## `pathlib`

These checks relate to the [pathlib](https://docs.python.org/3/library/pathlib.html)
standard library module.

## `performance`

These checks are supposted to find slow code that can be written faster. The threshold for
"fast" and "slow" are somewhat arbitrary and depend on the check, but in general you should
expect that a check in the `performance` category will make your code faster (and should never
make it slower).

## `pythonic`

This is a general catch-all for things which are "unpythonic". It differs from the
`readability` category because "unreadable" code can still be pythonic.

## `readability`

These checks aim to make existing code more readable. This can be subjective, but in general,
they reduce the horizontal or vertical length of your code, or make the underlying meaning
of the code more apparent.

## `scoping`

These checks have to do with Python's scoping rules. For more info on how Python's scoping
rules work, read [this article](https://realpython.com/python-scope-legb-rule/).

## `string`

These checks deal with usage of [`str`](https://docs.python.org/3/library/stdtypes.html#string-methods)
objects in Python.

## `set`

These checks deal with usage of [`set`](https://docs.python.org/3/tutorial/datastructures.html#sets)
objects in Python.

## `truthy`

These checks cover truthy and falsy operations in Python, primarily in the context of `assert` and `if`
statements.
