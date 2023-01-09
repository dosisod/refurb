from dataclasses import dataclass

from mypy.nodes import CallExpr, MemberExpr, NameExpr

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    A modern alternative to `os.getcwd()` is the `Path.cwd()` function:

    Bad:

    ```
    cwd = os.getcwd()
    ```

    Good:

    ```
    cwd = Path.cwd()
    ```
    """

    name = "use-pathlib-cwd"
    code = 104
    msg: str = "Replace `os.getcwd()` with `Path.cwd()`"
    categories = ["pathlib"]


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(callee=NameExpr(fullname=name)) | CallExpr(
            callee=MemberExpr(fullname=name)
        ) if name in ("os.getcwd", "os.getcwdb"):
            errors.append(
                ErrorInfo(
                    node.line,
                    node.column,
                    f"Replace `{name}()` with `Path.cwd()`",
                )
            )
