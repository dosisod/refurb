from dataclasses import dataclass

from mypy.nodes import (
    Block,
    CallExpr,
    ExpressionStmt,
    ForStmt,
    MemberExpr,
    NameExpr,
    Var,
    WithStmt,
)

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    When you want to write a list of lines to a file, don't call `.write()`
    for every line, use `.writelines()` instead:

    Bad:

    ```
    lines = ["line 1", "line 2", "line 3"]

    with open("file") as f:
        for line in lines:
            f.write(line)
    ```

    Good:

    ```
    lines = ["line 1", "line 2", "line 3"]

    with open("file") as f:
        f.writelines(lines)
    ```

    Note: If you have a more complex expression then just `lines`, you may
    need to use a list comprehension instead. For example:

    ```
    f.writelines(f"{line}\\n" for line in lines)
    ```
    """

    name = "use-writelines"
    code = 122
    msg: str = "Replace `for line in lines: f.write(line)` with `f.writelines(lines)`"  # noqa: E501
    categories = ["builtin", "readability"]


def check(node: WithStmt, errors: list[Error]) -> None:
    match node:
        case WithStmt(
            target=[NameExpr(node=Var(type=ty)) as resource],
            body=Block(
                body=[
                    ForStmt(
                        index=NameExpr(),
                        body=Block(
                            body=[
                                ExpressionStmt(
                                    expr=CallExpr(
                                        callee=MemberExpr(
                                            expr=NameExpr() as file,
                                            name="write",
                                        )
                                    )
                                )
                            ]
                        ),
                    ) as for_stmt
                ]
            ),
        ) if str(ty).startswith("io.") and resource.fullname == file.fullname:
            errors.append(ErrorInfo(for_stmt.line, for_stmt.column))
