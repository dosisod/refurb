from dataclasses import dataclass

from mypy.nodes import ConditionalExpr

from refurb.checks.common import is_equivalent, stringify
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Sometimes the ternary operator (aka, inline if statements) can be
    simplified to a single `or` expression.

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
    categories = ("logical", "readability")


def check(node: ConditionalExpr, errors: list[Error]) -> None:
    if is_equivalent(node.if_expr, node.cond):
        if_true = stringify(node.if_expr)
        if_false = stringify(node.else_expr)

        old = f"{if_true} if {if_true} else {if_false}"
        new = f"{if_true} or {if_false}"

        msg = f"Replace `{old}` with `{new}`"

        errors.append(ErrorInfo.from_node(node, msg))
