# Adding New Checks

This document is aimed at developers looking to contribute new checks to Refurb.
After reading this you should be better equipped to work with Refurb, including
Mypy internals, which are at the heart of Refurb.

## Setting Up

See the "[Developing](/README.md#developing)" section of the README to see how to
setup a dev environment for Refurb.

## Generating the Boilerplate

First things first, you will want to generate the boilerplate code using the `refurb gen`
command. See the "[Writing Your Own Check](/README.md#writing-your-own-check)" section
of the README for more info.

A few things to note:

* Place your check in a folder that corresponds to what it is checking. For example, if it
applies to string types, put it in the `string` folder. If it applies to the [pathlib](https://docs.python.org/3/library/pathlib.html)
module, put it in the `pathlib` folder.

* Base the filename of your check on what the check does to the code it checks. For example, FURB124
(`refurb/checks/logical/use_equal_chain.py`) is named `use_equal_chain` because it converts
the expression `x == y or x == z` to `x == y == z`. The resulting code uses a chain of equal
expressions, and it is named as such.

  * One exception is when your check is detecting something that you *shouldn't* be doing,
  in which case you should prefix it with `no_`. For example, the `no_del.py` check will check
  for usage of the `del` statement.

* Choose a prefix which is between 3-4 characters, and is uppercase alpha (regex: `[A-Z]{3,4}`).

* Make sure that the auto-generated error code id (the `code` field) is correct. It will try
to detect the next id based off of the supplied prefix, but if it cannot find it, it will default
to 100.

Also, if you are making a check for Refurb itself, remove the `suffix` line, which defaults
to `XYZ`. Deleting this will fallback to `FURB`, which is used for the built-in Refurb checks.

## Coming Up With An Idea

For the rest of this article, we will be creating the following check: Basically, it will
detect whenever you are comparing a floating point number using the `==` operator. For instance:

```python
x = 1.0
y = 2.0

z = (x + y) == 0.3
```

If you where to run the following code, `z` would be `False`, due to how floating point numbers
work (see [0.30000000000000004.com](https://0.30000000000000004.com/) for more info).

For this example, we will be writing our code in `refurb/checks/logical/no_float_cmp.py`, and
our error code id will be `132`. Your name, number, and idea should be different, but the general
idea is the same.

Let's get started!

## Figuring Out What to Do

The easiest way to see what you need to do is to create a small file with the code you want to
check against. For example, lets create a file called `tmp.py`, and put our code from above into
it:

```python
x = 1.0
y = 2.0

z = (x + y) == 0.3
```

Then, we will run `refurb tmp.py --debug --quiet`. You should see something like this:

```
MypyFile:1(
  tmp.py
  AssignmentStmt:1(
    NameExpr(x [tmp.x])
    FloatExpr(1.0)
    builtins.float)
  AssignmentStmt:2(
    NameExpr(y [tmp.y])
    FloatExpr(2.0)
    builtins.float)
  AssignmentStmt:4(
    NameExpr(z* [tmp.z])
    ComparisonExpr:4(
      ==
      OpExpr:4(
        +
        NameExpr(x [tmp.x])
        NameExpr(y [tmp.y]))
      FloatExpr(0.3))))
```

This is the [AST](https://en.wikipedia.org/wiki/Abstract_syntax_tree) representation of our code.
Some things to note:

* Files are represented with the `MypyFile` type.
* Each `MypyFile` contains a `Block`, which is a list of statements. In this case, we have
a bunch of `AssignmentStmt` statements.
* Each `AssignmentStmt` is composed of 2 major parts:
  * The `NameExpr`, which is the name/variable being assigned to
  * The expression being assigned: `FloatExpr`, `ComparisonExpr`, etc.

For our check, we only need to care about the `ComparisonExpr` part. Lets jump in!

## Writing the Check

We will start by updating the `check` function in our `no_float_cmp.py` file to the following:

```python
def check(node: ComparisonExpr, errors: list[Error]) -> None:
    match node:
        case ComparisonExpr():
            errors.append(ErrorInfo(node.line, node.column))
```

This code will basically emit an error whenever a `ComparisonExpr` is found, regardless of what
we are comparing.

Lets make sure it works first by running `refurb tmp.py` again. We should see an error like the
following:

```
tmp.py:4:5 [FURB132]: Your message here
```

Now lets add some test code to the `tmp.py` file to test that we are actually checking the code
we care about:

```python
x = 1.0
y = 2.0

# these should match

_ = x == 0.3
_ = (x + y) == 0.3

# these should not

_ = x <= 0.3
_ = x == 1
```

Notice how I switched the `z` variable to `_`. This is because `_` is a placeholder variable in Python,
and will gobble up any value you put into it. Since we cannot just write `(x + y) == 0.3` on a line all
by itself, we have to assign it to a variable instead [^1].

If we re-run, we get the following:

```
tmp.py:6:5 [FURB132]: Your message here
tmp.py:7:5 [FURB132]: Your message here
tmp.py:11:5 [FURB132]: Your message here
tmp.py:12:5 [FURB132]: Your message here
```

Lets fix that!

Basically, we only want to match on a `ComparisonExpr` that has an `==`, and a float
on either the left or right hand side. Lets go to the definition of the `ComparisonExpr`
class and see what we can find:

```python
class ComparisonExpr(Expression):
    """Comparison expression (e.g. a < b > c < d)."""

    __slots__ = ("operators", "operands", "method_types")

    operators: list[str]
    operands: list[Expression]
    # Inferred type for the operator methods (when relevant; None for 'is').
    method_types: list[mypy.types.Type | None]

    ...
```

Basically, a comparison expression can be a simple comparison, like `x == y`, or it can
be a more complex comparison, such as `x < y < z`. This is why we have a list of operators,
and a list of operands.

To start with, lets match the following:

```python
    match node:
        case ComparisonExpr(
            operators=["=="],
            operands=[FloatExpr(), _] | [_, FloatExpr()],
        ):
```

This will match any `ComparisonExpr` that has a `FloatExpr` on the left or right hand side
of an `==` expression. In this case, a `FloatExpr` is a floating point literal, such as `3.14`,
and not a `float` variable. The `|` is an "Or Pattern", meaning an array with a `FloatExpr` on
the left or right hand side will cause the pattern match to succeed. `_` is a placeholder meaning
any value can be there.

Now when we run, we get the following:

```
tmp.py:6:5 [FURB132]: Your message here
tmp.py:7:5 [FURB132]: Your message here
```

Much better!

One issue: The following code will not emit an error:

```python
_ = x == y == 0.3
```

This is because we only allow a `ComparisonExpr` if it has a single `==` operator. One way of
fixing it is by changing our check to the following:

```python
def check(node: ComparisonExpr, errors: list[Error]) -> None:
    match node:
        case ComparisonExpr(operators=operators, operands=operands):
            for oper, exprs in merge_comparison(operators, operands):
                if oper == "==":
                    for expr in exprs:
                        if isinstance(expr, FloatExpr):
                            errors.append(ErrorInfo(expr.line, expr.column))
```

Now in our `check` function, we:

1. Check if the operator is `==`
2. If it is, loop through the left and right hand expressions
3. If the expression is a `FloatExpr`, we emit an error

Here is the definition of our `merge_comparison` function:

```python
def merge_comparison(
    opers: list[str], exprs: list[Expression]
) -> Generator[tuple[str, tuple[Expression, Expression]], None, None]:
    exprs = exprs.copy()

    for oper in opers:
        yield (oper, (exprs[0], exprs[1]))

        exprs.pop(0)
```

The `merge_comparison` function will merge the operators and expressions into a list
of tuples which we can very easily loop over. For example, `1 < 2 == 3` would be converted into:

```
[("<", (1, 2), ("==", (2, 3)))]
```

Except that `1`, `2`, and `3` would be an `Expression` instead of a plain number.

That's it!

## Cleanup

Our check works, but it could be simplified. For example, we know `node` is a `ComparisonExpr`, and all
we are doing in the pattern match is pulling out the `operators` and `operands` fields, which we know
exist on `node`. We could re-write it like so:

```python
def check(node: ComparisonExpr, errors: list[Error]) -> None:
    for oper, exprs in merge_opers(node.operators, node.operands):
        if oper == "==":
            for expr in exprs:
                if isinstance(expr, FloatExpr):
                    errors.append(ErrorInfo(expr.line, expr.column))
```

The match statement is very good at checking very nested and complex structures, but in our case, we don't
need to use it.

Also, we should change the message in the `ErrorInfo` class to something like:

```python
    msg: str = "Don't compare float values with `==`"
```

## The Final Code

Here is the complete code for our check:

````python
from dataclasses import dataclass
from typing import Generator

from mypy.nodes import ComparisonExpr, Expression, FloatExpr

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    TODO: fill this in

    Bad:

    ```
    # TODO: fill this in
    ```

    Good:

    ```
    # TODO: fill this in
    ```
    """

    code = 132
    msg: str = "Don't compare float values with `==`"


def merge_opers(
    opers: list[str], exprs: list[Expression]
) -> Generator[tuple[str, tuple[Expression, Expression]], None, None]:
    exprs = exprs.copy()

    for oper in opers:
        yield (oper, (exprs[0], exprs[1]))

        exprs.pop(0)


def check(node: ComparisonExpr, errors: list[Error]) -> None:
    for oper, exprs in merge_opers(node.operators, node.operands):
        if oper == "==":
            for expr in exprs:
                if isinstance(expr, FloatExpr):
                    errors.append(ErrorInfo(expr.line, expr.column))
````

And the contents of our `tmp.py` testing file:

```python
x = 1.0
y = 2.0

# these should match

_ = x == 0.3
_ = (x + y) == 0.3
_ = x == y == 0.3

# these should not

_ = x <= 0.3
_ = x == 1
```

When we run, we get the following:

```
$ refurb tmp.py --quiet
tmp.py:6:10 [FURB132]: Don't compare float values with `==`
tmp.py:7:16 [FURB132]: Don't compare float values with `==`
tmp.py:8:15 [FURB132]: Don't compare float values with `==`
```

## Testing

This should be pretty easy because we have been testing all along! All we need to do now is copy our
code to the right place and we should be good to go:

```
$ cp tmp.py test/data/err_132.py
$ refurb test/data/err_132.py --quiet > test/data/err_132.txt
```

Now when we run `pytest`, all our tests should pass, and our coverage should be at 100%.

The last step is running `make` which will run all of our linters, type-checkers,
and so on.

## Fin

That's it for the most part! There are more complex features and techniques which I will be explaining
later on, but this will work as a good starting ground for anyone wanting to get started developing on
Refurb.

[^1]: We could write it on one line, but your linter might complain, and it is better to be
more explicit that "we do not want to use this value, please ignore".
