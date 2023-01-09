from dataclasses import dataclass

from mypy.nodes import CallExpr, MemberExpr, NameExpr, StrExpr

from refurb.error import Error

from .util import is_pathlike


@dataclass
class ErrorInfo(Error):
    """
    Don't use `open(x, "w").close()` if you just want to create an empty file,
    use the less confusing `Path.touch()` method instead.

    Bad:

    ```
    open("file.txt", "w").close()
    ```

    Good:

    ```
    from pathlib import Path

    Path("file.txt").touch()
    ```

    This check is disabled by default because `touch()` will throw a
    `FileExistsError` if the file already exists, and (at least on Linux) it
    sets different file permissions, meaning it is not a drop-in replacement.
    If you don't care about the file permissions or know that the file doesn't
    exist beforehand this check may be for you.
    """

    name = "use-pathlib-touch"
    enabled = False
    code = 151
    categories = ["pathlib"]


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=MemberExpr(
                expr=CallExpr(
                    callee=NameExpr(fullname="builtins.open"),
                    args=[arg, StrExpr(value=mode)],
                    arg_names=[_, None | "mode"],
                ),
                name="close",
            ),
            args=[],
        ) if "w" in mode:
            new = "x.touch()" if is_pathlike(arg) else "Path(x).touch()"

            errors.append(
                ErrorInfo(
                    node.line,
                    node.column,
                    f'Replace `open(x, "{mode}").close()` with `{new}`',
                )
            )
