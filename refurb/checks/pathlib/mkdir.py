from dataclasses import dataclass
from typing import cast

from mypy.nodes import CallExpr, MemberExpr

from refurb.error import Error

from .util import is_pathlike


@dataclass
class ErrorInfo(Error):
    """
    Use the `mkdir` function from the pathlib library instead of using the
    `mkdir` and `makedirs` functions from the `os` library: the pathlib library
    is more modern and provides better flexibility over the construction and
    manipulation of file paths.

    Bad:

    ```
    import os

    os.mkdir("new_folder")
    ```

    Good:

    ```
    from pathlib import Path

    Path("new_folder").mkdir()
    ```
    """

    name = "use-pathlib-mkdir"
    code = 150
    categories = ["pathlib"]


def create_error(node: CallExpr) -> list[Error]:
    old_args = ["x"]
    new_args = []

    fullname = cast(MemberExpr, node.callee).fullname
    is_makedirs = fullname == "os.makedirs"

    allowed_names = [None, "mode"]

    if is_makedirs:
        allowed_names.append("exist_ok")

    if len(node.args) > 1:
        if any(name not in allowed_names for name in node.arg_names):
            return []

        old_args.append("...")
        new_args.append("...")

    if is_makedirs:
        new_args.append("parents=True")

    new_args = ", ".join(new_args)

    expr = (
        f"x.mkdir({new_args})"
        if is_pathlike(node.args[0])
        else f"Path(x).mkdir({new_args})"
    )

    return [
        ErrorInfo(
            node.line,
            node.column,
            f"Replace `{fullname}({', '.join(old_args)})` with `{expr}`",
        )
    ]


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=MemberExpr(fullname="os.mkdir"), args=args
        ) if args:
            errors.extend(create_error(node))

        case CallExpr(
            callee=MemberExpr(fullname="os.makedirs"), args=args
        ) if args:
            errors.extend(create_error(node))
