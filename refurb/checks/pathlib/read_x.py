from dataclasses import dataclass
from typing import ClassVar

from mypy.nodes import (
    AssignmentStmt,
    Block,
    CallExpr,
    MemberExpr,
    NameExpr,
    StrExpr,
    WithStmt,
)

from refurb.error import Error


@dataclass
class ErrorUsePathlibRead(Error):
    """
    When you just want to save the contents of a file to a variable, using a
    `with` block is a bit overkill. A simpler alternative is to use pathlib's
    `read_text()` function:

    Bad:

    ```
    with open(filename) as f:
        contents = f.read()
    ```

    Good:

    ```
    contents = Path(filename).read_text()
    ```
    """

    code: ClassVar[int] = 101


def check(node: WithStmt, errors: list[Error]) -> None:
    match node:
        case WithStmt(
            expr=[CallExpr(callee=NameExpr(name="open"), args=args)],
            body=Block(
                body=[
                    AssignmentStmt(
                        rvalue=CallExpr(callee=MemberExpr(name="read"))
                    )
                ]
            ),
        ):
            is_binary = False
            options = ""

            match args:
                case [_, StrExpr(value=mode)] if "b" in mode:
                    options = f', "{mode}"'
                    is_binary = True

            func = "read_bytes" if is_binary else "read_text"

            errors.append(
                ErrorUsePathlibRead(
                    node.line,
                    node.column,
                    f"Use `y = Path(x).{func}()` instead of `with open(x{options}) as f: y = f.read()`",  # noqa: E501
                )
            )
