from dataclasses import dataclass

from mypy.nodes import Block, CallExpr, ComparisonExpr, ExpressionStmt, IfStmt, MemberExpr

from refurb.checks.common import get_mypy_type, is_equivalent, is_same_type, stringify
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    If you want to remove a value from a set regardless of whether it exists or
    not, use the `discard()` method instead of `remove()`:

    Bad:

    ```
    nums = {123, 456}

    if 123 in nums:
        nums.remove(123)
    ```

    Good:

    ```
    nums = {123, 456}

    nums.discard(123)
    ```
    """

    name = "use-set-discard"
    code = 132
    categories = ("readability", "set")


def check(node: IfStmt, errors: list[Error]) -> None:
    match node:
        case IfStmt(
            expr=[ComparisonExpr(operators=["in"], operands=[lhs, rhs])],
            body=[
                Block(
                    body=[
                        ExpressionStmt(
                            expr=CallExpr(
                                callee=MemberExpr(expr=expr, name="remove"),
                                args=[arg],
                            )
                        )
                    ]
                )
            ],
            else_body=None,
        ) if (
            is_equivalent(lhs, arg)
            and is_equivalent(rhs, expr)
            and is_same_type(get_mypy_type(expr), set)
        ):
            old = stringify(node)
            new = f"{stringify(expr)}.discard({stringify(arg)})"

            msg = f"Replace `{old}` with `{new}`"

            errors.append(ErrorInfo.from_node(node, msg))
