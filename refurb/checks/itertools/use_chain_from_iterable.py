from dataclasses import dataclass

from mypy.nodes import (
    ArgKind,
    CallExpr,
    GeneratorExpr,
    ListComprehension,
    ListExpr,
    RefExpr,
    SetComprehension,
)

from refurb.checks.common import stringify
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    When flattening a list of lists, use the `chain.from_iterable()` function
    from the `itertools` stdlib package. This function is faster than native
    list/generator comprehensions or using `sum()` with a list default.

    Bad:

    ```
    from itertools import chain

    rows = [[1, 2], [3, 4]]

    # using list comprehension
    flat = [col for row in rows for col in row]

    # using sum()
    flat = sum(rows, [])

    # using chain(*x)
    flat = chain(*rows)
    ```

    Good:

    ```
    from itertools import chain

    rows = [[1, 2], [3, 4]]

    flat = chain.from_iterable(rows)
    ```

    Note: `chain.from_iterable()` returns an iterator, which means you might
    need to wrap it in `list()` depending on your use case. Refurb cannot
    detect this (yet), so this is something you will need to keep in mind.

    Note: `chain(*x)` may be marginally faster/slower depending on the length
    of `x`. Since `*` might potentially expand to a lot of arguments, it is
    better to use `chain.from_iterable()` when you are unsure.
    """

    name = "use-chain-from-iterable"
    categories = ("itertools", "performance", "readability")
    code = 179


def is_flatten_generator(node: GeneratorExpr) -> bool:
    match node:
        case GeneratorExpr(
            left_expr=RefExpr(fullname=expr),
            sequences=[_, RefExpr(fullname=inner_source)],
            indices=[RefExpr(fullname=outer), RefExpr(fullname=inner)],
            is_async=[False, False],
            condlists=[[], []],
        ) if expr == inner and inner_source == outer:
            return True

    return False


# List of nodes we have already emitted errors for, since list comprehensions
# and their inner generators will emit 2 errors.
ignore = set[int]()


def check(
    node: ListComprehension | SetComprehension | GeneratorExpr | CallExpr,
    errors: list[Error],
) -> None:
    if id(node) in ignore:
        return

    match node:
        case ListComprehension(generator=g) if is_flatten_generator(g):
            old = "[... for ... in x for ... in ...]"
            new = "list(chain.from_iterable(x))"

            ignore.add(id(g))

        case SetComprehension(generator=g) if is_flatten_generator(g):
            old = "{... for ... in x for ... in ...}"
            new = "set(chain.from_iterable(x))"

            ignore.add(id(g))

        case GeneratorExpr() if is_flatten_generator(node):
            old = "... for ... in x for ... in ..."
            new = "chain.from_iterable(x)"

        case CallExpr(
            callee=RefExpr(fullname="builtins.sum"),
            args=[arg, ListExpr(items=[])],
        ):
            old = stringify(node)
            new = f"chain.from_iterable({stringify(arg)})"

        case CallExpr(
            callee=RefExpr(fullname="functools.reduce"),
            args=[op, arg] | [op, arg, ListExpr(items=[])],
        ):
            match op:
                case RefExpr(fullname="_operator.add" | "_operator.concat"):
                    pass

                case _:
                    return

            old = stringify(node)
            new = f"chain.from_iterable({stringify(arg)})"

        case CallExpr(
            callee=RefExpr(fullname="itertools.chain") as callee,
            args=[arg],
            arg_kinds=[ArgKind.ARG_STAR],
        ):
            old = stringify(node)
            new = f"{stringify(callee)}.from_iterable({stringify(arg)})"

        case _:
            return

    msg = f"Replace `{old}` with `{new}`"
    errors.append(ErrorInfo.from_node(node, msg))
