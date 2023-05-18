from dataclasses import dataclass

from mypy.nodes import CallExpr, RefExpr, StrExpr

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
    categories = ("pathlib", "readability")


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            args=[StrExpr(value="." | "" as value)],
            callee=RefExpr(fullname="pathlib.Path"),
        ):
            errors.append(
                ErrorInfo.from_node(
                    node, f'Replace `Path("{value}")` with `Path()`'
                )
            )
