from dataclasses import dataclass

from mypy.nodes import (
    Block,
    CallExpr,
    Expression,
    ExpressionStmt,
    ForStmt,
    MemberExpr,
    NameExpr,
    WithStmt,
)

from refurb.checks.common import get_mypy_type, is_equivalent, is_subclass, stringify
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    r"""
    When you want to write a list of lines to a file, don't call `.write()`
    for every line, use `.writelines()` instead:

    Bad:

    ```
    lines = ["line 1\n", "line 2\n", "line 3\n"]

    with open("file") as f:
        for line in lines:
            f.write(line)
    ```

    Good:

    ```
    lines = ["line 1\n", "line 2\n", "line 3\n"]

    with open("file") as f:
        f.writelines(lines)
    ```
    """

    name = "use-writelines"
    code = 122
    categories = ("builtin", "readability")


def is_file_object(f: Expression) -> bool:
    return is_subclass(get_mypy_type(f), "io.IOBase")


def check(node: WithStmt, errors: list[Error]) -> None:
    match node:
        case WithStmt(
            target=[NameExpr() as f],
            body=Block(
                body=[
                    ForStmt(
                        index=NameExpr() as for_target,
                        expr=source,
                        body=Block(
                            body=[
                                ExpressionStmt(
                                    expr=CallExpr(
                                        callee=MemberExpr(
                                            expr=NameExpr() as write_base,
                                            name="write",
                                        ),
                                        args=[write_arg],
                                    )
                                )
                            ]
                        ),
                        is_async=False,
                        else_body=None,
                    ) as for_stmt
                ]
            ),
        ) if is_file_object(f) and is_equivalent(f, write_base):
            old = stringify(for_stmt)

            if is_equivalent(for_target, write_arg):
                new = stringify(source)
            else:
                new = f"{stringify(write_arg)} for {stringify(for_target)} in {stringify(source)}"

            msg = f"Replace `{old}` with `{stringify(f)}.writelines({new})`"

            errors.append(ErrorInfo.from_node(for_stmt, msg))
