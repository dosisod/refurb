from dataclasses import dataclass

from mypy.nodes import CallExpr, MemberExpr, NameExpr

from refurb.checks.pathlib.util import is_pathlike
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    When removing a file, use the more modern `Path.unlink()` method instead of
    `os.remove()` or `os.unlink()`: The `pathlib` module allows for more
    flexibility when it comes to traversing folders, building file paths, and
    accessing/modifying files.

    Bad:

    ```
    import os

    os.remove("filename")
    ```

    Good:

    ```
    from pathlib import Path

    Path("filename").unlink()
    ```
    """

    name = "use-pathlib-unlink"
    code = 144
    categories = ["pathlib"]


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=(MemberExpr() | NameExpr()) as expr,
            args=[arg],
        ) if expr.fullname in ("os.remove", "os.unlink"):
            replace = "x.unlink()" if is_pathlike(arg) else "Path(x).unlink()"

            errors.append(
                ErrorInfo(
                    node.line,
                    node.column,
                    f"Replace `os.{expr.name}(x)` with `{replace}`",
                )
            )
