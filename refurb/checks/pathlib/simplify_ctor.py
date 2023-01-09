from dataclasses import dataclass

from mypy.nodes import CallExpr, NameExpr, StrExpr

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    The Path() constructor defaults to the current directory, so don't pass the
    current directory (".") explicitly.

    Bad:

    ```
    file = Path(".")
    ```

    Good:

    ```
    file = Path()
    ```
    """

    name = "simplify-path-constructor"
    code = 153
    msg: str = 'Replace `Path(".")` with `Path()`'
    categories = ["pathlib", "readability"]


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            args=[StrExpr(value=".")],
            callee=NameExpr(fullname="pathlib.Path"),
        ):
            errors.append(ErrorInfo(node.line, node.column))
