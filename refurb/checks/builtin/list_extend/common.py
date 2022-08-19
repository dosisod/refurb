from dataclasses import dataclass

from mypy.nodes import (
    CallExpr,
    ExpressionStmt,
    MemberExpr,
    NameExpr,
    Statement,
)

from refurb.error import Error


@dataclass
class ErrorUseListExtend(Error):
    """
    When appending multiple values to a list, you can use the `.extend()`
    method to add an iterable to the end of an existing list. This way, you
    don't have to call `.append()` on every element:

    Bad:

    ```
    nums = [1, 2, 3]

    nums.append(4)
    nums.append(5)
    nums.append(6)
    ```

    Good:

    ```
    nums = [1, 2, 3]

    nums.extend((4, 5, 6))
    ```
    """

    code = 113
    msg: str = "Use `x.extend(...)` instead of repeatedly calling `x.append()`"


def check_stmts(stmts: list[Statement], errors: list[Error]) -> None:
    last_append_name = ""

    for stmt in stmts:
        match stmt:
            case ExpressionStmt(
                expr=CallExpr(
                    callee=MemberExpr(expr=NameExpr(name=name), name="append")
                )
            ):
                if name == last_append_name:
                    errors.append(ErrorUseListExtend(stmt.line, stmt.column))

                last_append_name = name

            case _:
                last_append_name = ""
