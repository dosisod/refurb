from dataclasses import dataclass

from mypy.nodes import OpExpr

from refurb.checks.common import get_common_expr_in_comparison_chain
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    When checking that multiple objects are equal to each other, don't use
    an `and` expression. Use a comparison chain instead, for example:

    Bad:

    ```
    if x == y and x == z:
        pass
    ```

    Good:

    ```
    if x == y == z:
        pass
    ```

    Note: if `x` depends on side-effects, then this check should be ignored.
    """

    code = 124
    categories = ["logical", "readability"]


def create_message(indices: tuple[int, int]) -> str:
    names = ["x", "y", "z"]
    names.insert(indices[1], names[indices[0]])

    expr = f"{names[0]} == {names[1]} and {names[2]} == {names[3]}"

    return f"Replace `{expr}` with `x == y == z`"


def check(node: OpExpr, errors: list[Error]) -> None:
    if data := get_common_expr_in_comparison_chain(node, oper="and"):
        expr, indices = data

        errors.append(
            ErrorInfo(expr.line, expr.column, create_message(indices))
        )
