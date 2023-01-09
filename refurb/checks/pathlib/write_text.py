from dataclasses import dataclass

from mypy.nodes import (
    Block,
    CallExpr,
    ExpressionStmt,
    MemberExpr,
    NameExpr,
    StrExpr,
    WithStmt,
)

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    When you just want to save some contents to a file, using a `with` block is
    a bit overkill. Instead you can use pathlib's `write_text()` function:

    Bad:

    ```
    with open(filename, "w") as f:
        f.write("hello world")
    ```

    Good:

    ```
    Path(filename).write_text("hello world")
    ```
    """

    name = "use-pathlib-write-text-write-bytes"
    code = 103
    categories = ["pathlib"]


def check(node: WithStmt, errors: list[Error]) -> None:
    match node:
        case WithStmt(
            expr=[
                CallExpr(
                    callee=NameExpr(name="open"), args=[_, StrExpr(value=mode)]
                )
            ],
            target=[NameExpr(name=with_name)],
            body=Block(
                body=[
                    ExpressionStmt(
                        expr=CallExpr(
                            callee=MemberExpr(
                                expr=NameExpr(name=write_name), name="write"
                            )
                        )
                    )
                ]
            ),
        ) if with_name == write_name and "w" in mode:
            func = "write_bytes" if ("b" in mode) else "write_text"

            errors.append(
                ErrorInfo(
                    node.line,
                    node.column,
                    f"Replace `with open(x, ...) as f: f.write(y)` with `Path(x).{func}(y)`",  # noqa: E501
                )
            )
