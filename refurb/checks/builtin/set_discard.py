from dataclasses import dataclass

from mypy.nodes import (
    Block,
    CallExpr,
    ComparisonExpr,
    ExpressionStmt,
    IfStmt,
    MemberExpr,
    NameExpr,
    Var,
)

from refurb.checks.common import is_equivalent
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    If you want to remove a value from a set regardless of whether it exists or
    not, use the `discard()` method instead of `remove()`:

    Bad:

    ```
    nums = set((123, 456))

    if 123 in nums:
        nums.remove(123)
    ```

    Good:

    ```
    nums = set((123, 456))

    nums.discard(123)
    ```
    """

    name = "use-set-discard"
    code = 132
    msg: str = "Replace `if x in s: s.remove(x)` with `s.discard(x)`"
    categories = ["readability", "set"]


def check(node: IfStmt, errors: list[Error]) -> None:
    match node:
        case IfStmt(
            expr=[ComparisonExpr(operators=["in"], operands=[lhs, rhs])],
            body=[
                Block(
                    body=[
                        ExpressionStmt(
                            expr=CallExpr(
                                callee=MemberExpr(
                                    expr=NameExpr(node=Var(type=ty)) as expr,
                                    name="remove",
                                ),
                                args=[arg],
                            )
                        )
                    ]
                )
            ],
        ) if (
            is_equivalent(lhs, arg)
            and is_equivalent(rhs, expr)
            and str(ty).startswith("builtins.set[")
        ):
            errors.append(ErrorInfo(node.line, node.column))
