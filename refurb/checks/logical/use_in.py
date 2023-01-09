from dataclasses import dataclass

from mypy.nodes import OpExpr

from refurb.checks.common import get_common_expr_in_comparison_chain
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    When comparing a value to multiple possible options, don't use multiple
    `or` checks, use a single `in` expr:

    Bad:

    ```
    if x == "abc" or x == "def":
        pass
    ```

    Good:

    ```
    if x in ("abc", "def"):
        pass
    ```

    Note: This should not be used if the operands depend on boolean short
    circuiting, since the operands will be eagerly evaluated. This is primarily
    useful for comparing against a range of constant values.
    """

    name = "use-in-oper"
    code = 108
    categories = ["logical", "readability"]


def create_message(indices: tuple[int, int]) -> str:
    names = ["x", "y", "z"]
    common_name = names[indices[0]]
    names.insert(indices[1], common_name)

    old = f"{names[0]} == {names[1]} or {names[2]} == {names[3]}"

    names = [name for name in names if name != common_name]
    new = f"{common_name} in ({', '.join(names)})"

    return f"Replace `{old}` with `{new}`"


def check(node: OpExpr, errors: list[Error]) -> None:
    if data := get_common_expr_in_comparison_chain(node, oper="or"):
        expr, indices = data

        errors.append(
            ErrorInfo(expr.line, expr.column, create_message(indices))
        )
