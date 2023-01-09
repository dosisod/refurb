from dataclasses import dataclass

from mypy.nodes import AssignmentStmt, Block, MypyFile, NameExpr, Statement

from refurb.checks.common import check_block_like
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    You don't need to use a temporary variable to swap 2 variables, you can use
    tuple unpacking instead:

    Bad:

    ```
    temp = x
    x = y
    y = tmp
    ```

    Good:

    ```
    x, y = y, x
    ```
    """

    name = "use-tuple-unpack-swap"
    code = 128
    msg: str = "Use tuple unpacking instead of temporary variables to swap values"  # noqa: E501
    categories = ["readability"]


def check(node: Block | MypyFile, errors: list[Error]) -> None:
    check_block_like(check_stmts, node, errors)


def check_stmts(stmts: list[Statement], errors: list[Error]) -> None:
    assignments = []

    for stmt in stmts:
        if isinstance(stmt, AssignmentStmt):
            assignments.append(stmt)

        else:
            assignments = []

        if len(assignments) == 3:
            match assignments:
                case [
                    AssignmentStmt(
                        lvalues=[NameExpr() as a], rvalue=NameExpr() as b
                    ),
                    AssignmentStmt(
                        lvalues=[NameExpr() as c], rvalue=NameExpr() as d
                    ),
                    AssignmentStmt(
                        lvalues=[NameExpr() as e], rvalue=NameExpr() as f
                    ),
                ] if (
                    a.name == f.name and b.name == c.name and d.name == e.name
                ):
                    errors.append(ErrorInfo(a.line, a.column))

                    assignments = []

                case _:
                    assignments.pop(0)
