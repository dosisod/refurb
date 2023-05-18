from dataclasses import dataclass

from mypy.nodes import ComparisonExpr, ListExpr, TupleExpr

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
            operands=[_, ListExpr() | TupleExpr() as expr],
        ) if len(expr.items) == 1:
            new_oper = "==" if oper == "in" else "!="

            if isinstance(expr, ListExpr):
                msg = f"Replace `x {oper} [y]` with `x {new_oper} y`"
            else:
                msg = f"Replace `x {oper} (y,)` with `x {new_oper} y`"

            errors.append(ErrorInfo.from_node(node, msg))
