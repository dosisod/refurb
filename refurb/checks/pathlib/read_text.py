from dataclasses import dataclass

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
class ErrorUsePathlibReadText(Error):
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

    code = 101


def check(node: WithStmt, errors: list[Error]) -> None:
    match node:
        case WithStmt(
            expr=[CallExpr(callee=NameExpr(name="open"), args=args)],
            target=[NameExpr(name=with_name)],
            body=Block(
                body=[
                    AssignmentStmt(
                        rvalue=CallExpr(
                            callee=MemberExpr(
                                expr=NameExpr(name=read_name), name="read"
                            )
                        )
                    )
                ]
            ),
        ) if with_name == read_name:
            is_binary = False

            match args:
                case [_, StrExpr(value=mode)] if "b" in mode:
                    is_binary = True

            func = "read_bytes" if is_binary else "read_text"

            errors.append(
                ErrorUsePathlibReadText(
                    node.line,
                    node.column,
                    f"Use `y = Path(x).{func}()` instead of `with open(x, ...) as f: y = f.read()`",  # noqa: E501
                )
            )
