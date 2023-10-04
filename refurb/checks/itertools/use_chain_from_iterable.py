from dataclasses import dataclass

from mypy.nodes import (
    ArgKind,
    CallExpr,
    GeneratorExpr,
    ListExpr,
    NameExpr,
    RefExpr,
)

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    When flattening an list of lists, use the `chain.from_iterable` function
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

    flat = chain.from_iterable(*rows)
    ```

    Note: `chain(*x)` may be marginally faster/slower depending on the length
    of `x`. Since `*` might potentially expand to a lot of arguments, it is
    better to use `chain.from_iterable()` when you are unsure.
    """

    name = "use-chain-from-iterable"
    categories = ("itertools", "performance", "readability")
    code = 179


def check(node: GeneratorExpr | CallExpr, errors: list[Error]) -> None:
    match node:
        case GeneratorExpr(
            left_expr=RefExpr(fullname=expr),
            sequences=[_, RefExpr(fullname=inner_source)],
            indices=[RefExpr(fullname=outer), RefExpr(fullname=inner)],
            is_async=[False, False],
            condlists=[[], []],
        ) if expr == inner and inner_source == outer:
            old = "... for ... in x for ... in ..."
            new = "chain.from_iterable(x)"

            msg = f"Replace `{old}` with `{new}`"

            errors.append(ErrorInfo.from_node(node, msg))

        case CallExpr(
            callee=RefExpr(fullname="builtins.sum"),
            args=[_, ListExpr(items=[])],
        ):
            old = "sum(x, [])"
            new = "chain.from_iterable(x)"

            msg = f"Replace `{old}` with `{new}`"

            errors.append(ErrorInfo.from_node(node, msg))

        case CallExpr(
            callee=RefExpr(fullname="itertools.chain") as callee,
            args=[_],
            arg_kinds=[ArgKind.ARG_STAR],
        ):
            chain = (
                "chain" if isinstance(callee, NameExpr) else "itertools.chain"
            )

            old = f"{chain}(*x)"
            new = f"{chain}.from_iterable(x)"

            msg = f"Replace `{old}` with `{new}`"

            errors.append(ErrorInfo.from_node(node, msg))
