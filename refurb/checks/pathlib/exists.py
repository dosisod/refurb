from dataclasses import dataclass

from mypy.nodes import CallExpr, MemberExpr, NameExpr

from refurb.checks.pathlib.util import is_pathlike
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    When checking whether a file exists or not, try and use the more modern
    `pathlib` module instead of `os.path`.

    Bad:

    ```
    import os

    if os.path.exists("filename"):
        pass
    ```

    Good:

    ```
    from pathlib import Path

    if Path("filename").exists():
        pass
    ```
    """

    code = 141
    categories = ["pathlib"]


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=(MemberExpr() | NameExpr()) as expr,
            args=[arg],
        ) if expr.fullname == "genericpath.exists":
            replace = "x.exists()" if is_pathlike(arg) else "Path(x).exists()"

            errors.append(
                ErrorInfo(
                    node.line,
                    node.column,
                    f"Replace `os.path.exists(x)` with `{replace}`",
                )
            )
