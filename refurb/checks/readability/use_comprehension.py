from dataclasses import dataclass

from mypy.nodes import (
    AssignmentExpr,
    AssignmentStmt,
    Block,
    CallExpr,
    ExpressionStmt,
    ForStmt,
    IfStmt,
    ListExpr,
    MemberExpr,
    MypyFile,
    NameExpr,
    Statement,
)

from refurb.checks.common import ReadCountVisitor, check_block_like
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    When constructing a new list it is usually more performant to use a list
    comprehension, and in some cases, it can be more readable.

    Bad:

    ```
    nums = [1, 2, 3, 4]
    odds = []

    for num in nums:
        if num % 2:
            odds.append(num)
    ```

    Good:

    ```
    nums = [1, 2, 3, 4]
    odds = [num for num in nums if num % 2]
    ```
    """

    name = "use-list-comprehension"
    code = 138
    msg: str = "Consider using list comprehension"
    categories = ["performance", "readability"]


def check(node: Block | MypyFile, errors: list[Error]) -> None:
    check_block_like(check_stmts, node, errors)


def get_append_func_callee_name(expr: Statement) -> NameExpr | None:
    match expr:
        case ExpressionStmt(
            expr=CallExpr(
                callee=MemberExpr(
                    expr=NameExpr() as name,
                    name="append",
                )
            )
        ):
            return name

    return None


def check_stmts(stmts: list[Statement], errors: list[Error]) -> None:
    assign: NameExpr | None = None

    for stmt in stmts:
        if assign:
            match stmt:
                case ForStmt(
                    body=Block(
                        body=[
                            IfStmt(
                                expr=[if_expr],
                                body=[Block(body=[stmt])],
                                else_body=None,
                            )
                        ]
                    )
                ) if (
                    (name := get_append_func_callee_name(stmt))
                    and name.fullname == assign.fullname
                    and not isinstance(if_expr, AssignmentExpr)
                ):
                    name_visitor = ReadCountVisitor(name)
                    stmt.accept(name_visitor)

                    if name_visitor.read_count == 1:
                        errors.append(ErrorInfo(assign.line, assign.column))

                case ForStmt(body=Block(body=[stmt])) if (
                    (name := get_append_func_callee_name(stmt))
                    and name.fullname == assign.fullname
                ):
                    name_visitor = ReadCountVisitor(name)
                    stmt.accept(name_visitor)

                    if name_visitor.read_count == 1:
                        errors.append(ErrorInfo(assign.line, assign.column))

            assign = None

        match stmt:
            case AssignmentStmt(
                lvalues=[NameExpr() as name],
                rvalue=ListExpr(items=[]),
            ):
                assign = name
