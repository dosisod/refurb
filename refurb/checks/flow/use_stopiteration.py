from dataclasses import dataclass

from mypy.nodes import (
    AssignmentStmt,
    Block,
    CallExpr,
    ComparisonExpr,
    IfStmt,
    MypyFile,
    NameExpr,
    RaiseStmt,
    RefExpr,
    Statement,
)

from refurb.checks.common import check_block_like, is_equivalent, stringify
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    When using `next()` with a default value and then checking for that
    value to raise an exception, use a `try`/`except StopIteration` block
    instead. This avoids the edge case where the iterator legitimately
    yields the sentinel value:

    Bad:

    ```
    x = next((i for i in lst if i > 0), None)
    if x is None:
        raise ValueError("no positive items")
    ```

    Good:

    ```
    try:
        x = next(i for i in lst if i > 0)
    except StopIteration:
        raise ValueError("no positive items")
    ```
    """

    name = "use-stopiteration"
    code = 194
    categories = ("readability",)
    msg: str = "Replace `next()` with default + check with `try`/`except StopIteration`"


def check(node: Block | MypyFile, errors: list[Error]) -> None:
    check_block_like(check_stmts, node, errors)


def check_stmts(stmts: list[Statement], errors: list[Error]) -> None:
    for i, stmt in enumerate(stmts):
        if i + 1 >= len(stmts):
            break

        next_stmt = stmts[i + 1]

        match (stmt, next_stmt):
            case (
                AssignmentStmt(
                    lvalues=[NameExpr() as target],
                    rvalue=CallExpr(
                        callee=RefExpr(fullname="builtins.next"),
                        args=[_, default_arg],
                    ),
                ),
                IfStmt(
                    expr=[
                        ComparisonExpr(
                            operators=[op],
                            operands=[if_lhs, if_rhs],
                        )
                    ],
                    body=[Block(body=[RaiseStmt()])],
                    else_body=None,
                ),
            ) if (
                op in ("is", "==")
                and (
                    (is_equivalent(if_lhs, target) and is_equivalent(if_rhs, default_arg))
                    or (is_equivalent(if_rhs, target) and is_equivalent(if_lhs, default_arg))
                )
            ):
                errors.append(
                    ErrorInfo.from_node(
                        stmt,
                        f"Replace `{stringify(target)} = next(..., {stringify(default_arg)})` "
                        f"with `try`/`except StopIteration`",
                    )
                )
