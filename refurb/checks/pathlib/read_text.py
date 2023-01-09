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
class ErrorInfo(Error):
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

    name = "use-pathlib-read-text-read-bytes"
    code = 101
    categories = ["pathlib"]


def check(node: WithStmt, errors: list[Error]) -> None:
    match node:
        case WithStmt(
            expr=[
                CallExpr(
                    callee=NameExpr(name="open"),
                    args=args,
                    arg_names=arg_names,
                )
            ],
            target=[NameExpr(name=with_name)],
            body=Block(
                body=[
                    AssignmentStmt(
                        rvalue=CallExpr(
                            callee=MemberExpr(
                                expr=NameExpr(name=read_name), name="read"
                            ),
                            args=[],
                        )
                    )
                ]
            ),
        ) if with_name == read_name:
            func = "read_text"
            read_text_params = ""
            with_params = ""

            for i, name in enumerate(arg_names[1:], start=1):
                if name in (None, "mode"):
                    with_params = ", ..."

                    match args[i]:
                        case StrExpr(value=mode) if "b" in mode:
                            func = "read_bytes"

                elif name in ("encoding", "errors"):
                    read_text_params = "..."
                    with_params = ", ..."

                else:
                    return

            errors.append(
                ErrorInfo(
                    node.line,
                    node.column,
                    f"Replace `with open(x{with_params}) as f: y = f.read()` with `y = Path(x).{func}({read_text_params})`",  # noqa: E501
                )
            )
