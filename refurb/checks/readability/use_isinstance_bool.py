from dataclasses import dataclass

from mypy.nodes import ComparisonExpr, Expression, ListExpr, NameExpr, SetExpr, TupleExpr

from refurb.checks.common import stringify
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Don't check if a value is `True` or `False` using `in`, use an
    `isinstance()` call.

    Bad:

    ```
    if value in {True, False}:
        pass
    ```

    Good:

    ```
    if isinstance(value, bool):
        pass
    ```
    """

    name = "use-isinstance-bool"
    code = 191
    categories = ("readability",)


# TODO: move to common
def is_true(expr: Expression) -> bool:
    match expr:
        case NameExpr(fullname="builtins.True"):
            return True

    return False


def is_false(expr: Expression) -> bool:
    match expr:
        case NameExpr(fullname="builtins.False"):
            return True

    return False


def check(node: ComparisonExpr, errors: list[Error]) -> None:
    match node:
        case ComparisonExpr(
            operators=["in" | "not in" as op],
            operands=[
                lhs,
                SetExpr(items=[t, f]) | TupleExpr(items=[t, f]) | ListExpr(items=[t, f]),
            ],
        ) if (is_true(t) and is_false(f)) or (is_false(t) and is_true(f)):
            old = stringify(node)
            new = f"isinstance({stringify(lhs)}, bool)"

            if op == "not in":
                new = f"not {new}"

            msg = f"Replace `{old}` with `{new}`"

            errors.append(ErrorInfo.from_node(node, msg))
