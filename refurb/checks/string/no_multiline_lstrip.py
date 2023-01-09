from dataclasses import dataclass

from mypy.nodes import CallExpr, MemberExpr, StrExpr

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    '''
    If you want to define a multi-line string but don't want a leading newline,
    use a continuation character ('\\'), don't use `.lstrip()`.

    Bad:

    ```
    """
    This is some docstring
    """.lstrip()
    ```

    Good:

    ```
    """\\
    This is some docstring
    """
    ```
    '''

    name = "no-multiline-lstrip"
    code = 139
    msg: str = 'Replace `"""\\n...""".lstrip()` with `"""\\..."""`'
    categories = ["readability"]


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=MemberExpr(
                expr=StrExpr(value=value),
                name="lstrip",
            ),
            args=[] | [StrExpr(value="\n")],
        ) if (
            node.line != node.end_line
            and len(value) > 1
            and value.startswith("\n")
            and not value[1].isspace()
        ):
            errors.append(
                ErrorInfo(
                    node.line,
                    node.column,
                )
            )
