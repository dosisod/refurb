from dataclasses import dataclass

from mypy.nodes import ConditionalExpr

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Sometimes ternary (aka, inline if statements) can be simplified to a single
    or expression.

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

    code = 110
    msg: str = "Use `x or y` instead of `x if x else y`"


def check(node: ConditionalExpr, errors: list[Error]) -> None:
    if str(node.if_expr) == str(node.cond):
        errors.append(ErrorInfo(node.line, node.column))
