from dataclasses import dataclass

from mypy.nodes import CallExpr, RefExpr

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
    categories = ("pathlib",)


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(callee=RefExpr(fullname=fullname)) if fullname in (
            "os.getcwd",
            "os.getcwdb",
        ):
            errors.append(
                ErrorInfo.from_node(
                    node, f"Replace `{fullname}()` with `Path.cwd()`"
                )
            )
