from dataclasses import dataclass
from typing import ClassVar

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
class ErrorUseWithSuffix(Error):
    """
    A common operation is changing the extention of a file. If you have an
    existing `Path` object, you don't need to convert it to a string, slice
    it, and append a new extention. Instead, use the `with_suffix()` function:

    Bad:

    ```
    new_filepath = str(Path("file.txt"))[:4] + ".md"
    ```

    Good:

    ```
    new_filepath = Path("file.txt").with_suffix(".md")
    ```
    """

    code: ClassVar[int] = 100
    msg: str = "Use `Path(x).with_suffix(y)` instead of slice and concat"  # noqa: E501


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
            errors.append(ErrorUseWithSuffix(node.line, node.column))
