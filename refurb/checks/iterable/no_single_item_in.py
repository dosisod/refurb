from dataclasses import dataclass

from mypy.nodes import ComparisonExpr, ListExpr, SetExpr, TupleExpr

from refurb.checks.common import stringify
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Don't use `in` to check against a single value, use `==` instead:

    Bad:

    ```
    if name in ("bob",):
        pass
    ```

    Good:

    ```
    if name == "bob":
        pass
    ```
    """

    name = "no-single-item-in"
    code = 171
    categories = ("iterable", "readability")


def check(node: ComparisonExpr, errors: list[Error]) -> None:
    match node:
        case ComparisonExpr(
            operators=["in" | "not in" as oper],
            operands=[lhs, ListExpr() | TupleExpr() | SetExpr() as expr],
        ) if len(expr.items) == 1:
            new_oper = "==" if oper == "in" else "!="

            new = f"{stringify(lhs)} {new_oper} {stringify(expr.items[0])}"

            msg = f"Replace `{stringify(node)}` with `{new}`"

            errors.append(ErrorInfo.from_node(node, msg))
