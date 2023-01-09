from dataclasses import dataclass

from mypy.nodes import (
    CallExpr,
    IndexExpr,
    NameExpr,
    OpExpr,
    SliceExpr,
    StrExpr,
)

from refurb.error import Error

from .util import is_pathlike


@dataclass
class ErrorInfo(Error):
    """
    A common operation is changing the extension of a file. If you have an
    existing `Path` object, you don't need to convert it to a string, slice
    it, and append a new extension. Instead, use the `with_suffix()` function:

    Bad:

    ```
    new_filepath = str(Path("file.txt"))[:4] + ".md"
    ```

    Good:

    ```
    new_filepath = Path("file.txt").with_suffix(".md")
    ```
    """

    name = "use-pathlib-with-suffix"
    code = 100
    msg: str = "Use `Path(x).with_suffix(y)` instead of slice and concat"  # noqa: E501
    categories = ["pathlib"]


def check(node: OpExpr, errors: list[Error]) -> None:
    match node:
        case OpExpr(
            op="+",
            left=IndexExpr(
                base=CallExpr(
                    callee=NameExpr(name="str"),
                    args=[arg],
                ),
                index=SliceExpr(begin_index=None),
            ),
            right=StrExpr(),
        ) if is_pathlike(arg):
            errors.append(ErrorInfo(arg.line, arg.column))
