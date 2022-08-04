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
