from dataclasses import dataclass
from typing import cast

from mypy.nodes import (
    AssignmentStmt,
    Block,
    CallExpr,
    ExpressionStmt,
    MemberExpr,
    MypyFile,
    NameExpr,
    RefExpr,
    Statement,
)

from refurb.checks.common import check_block_like, stringify
from refurb.checks.hashlib.use_hexdigest import HASHLIB_ALGOS
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    You can pass data into `hashlib` constructors, so instead of creating a
    hash object and immediately updating it, pass the data directly.

    Bad:

    ```
    from hashlib import sha512

    h = sha512()
    h.update(b"data")
    ```

    Good:

    ```
    from hashlib import sha512

    h = sha512(b"data")
    ```
    """

    name = "simplify-hashlib-ctor"
    categories = ("hashlib", "readability")
    code = 182


def check(node: Block | MypyFile, errors: list[Error]) -> None:
    check_block_like(check_stmts, node, errors)


def check_stmts(stmts: list[Statement], errors: list[Error]) -> None:
    assignment: AssignmentStmt | None = None
    var: RefExpr | None = None

    for stmt in stmts:
        match stmt:
            case AssignmentStmt(
                lvalues=[NameExpr() as lhs],
                rvalue=CallExpr(callee=RefExpr(fullname=fn), args=[]),
            ) if fn in HASHLIB_ALGOS:
                assignment = stmt
                var = lhs

            case ExpressionStmt(
                expr=CallExpr(
                    callee=MemberExpr(
                        expr=RefExpr(fullname=fullname, name=lhs),  # type: ignore
                        name="update",
                    ),
                    args=[arg],
                )
            ) if assignment and var and var.fullname == fullname:
                func_name = stringify(cast("CallExpr", assignment.rvalue).callee)

                data = stringify(arg)

                old = f"{lhs} = {func_name}(); {lhs}.update({data})"
                new = f"{lhs} = {func_name}({data})"

                msg = f"Replace `{old}` with `{new}`"

                errors.append(ErrorInfo.from_node(assignment, msg))

            case _:
                assignment = None
