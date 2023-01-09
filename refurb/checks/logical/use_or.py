from dataclasses import dataclass

from mypy.nodes import ConditionalExpr

from refurb.checks.common import is_equivalent
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Sometimes ternary (aka, inline if statements) can be simplified to a single
    `or` expression.

    Bad:

    ```
    z = x if x else y
    ```

    Good:

    ```
    z = x or y
    ```

    Note: if `x` depends on side-effects, then this check should be ignored.
    """

    name = "use-or-oper"
    code = 110
    msg: str = "Replace `x if x else y` with `x or y`"
    categories = ["logical", "readability"]


def check(node: ConditionalExpr, errors: list[Error]) -> None:
    if is_equivalent(node.if_expr, node.cond):
        errors.append(ErrorInfo(node.line, node.column))
