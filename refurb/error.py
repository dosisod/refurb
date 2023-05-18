from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from pathlib import Path

    from mypy.nodes import Node


@dataclass(frozen=True)
class ErrorCode:
    """
    This class represents an error code id which can be used to enable and
    disable errors in Refurb. The `path` field is used to tell Refurb that a
    particular error should only apply to a given path instead of all paths,
    which is the default.
    """

    id: int
    prefix: str = "FURB"
    path: Path | None = None

    @classmethod
    def from_error(cls, err: type[Error]) -> ErrorCode:
        return ErrorCode(err.code, err.prefix)

    def __str__(self) -> str:
        return f"{self.prefix}{self.id}"


@dataclass(frozen=True)
class ErrorCategory:
    value: str
    path: Path | None = None


ErrorClassifier = ErrorCategory | ErrorCode


@dataclass
class Error:
    enabled: ClassVar[bool] = True
    name: ClassVar[str | None] = None
    prefix: ClassVar[str] = "FURB"
    categories: ClassVar[tuple[str, ...]] = ()
    code: ClassVar[int]
    line: int
    column: int
    msg: str
    filename: str | None = None
    line_end: int | None = None
    column_end: int | None = None

    def __str__(self) -> str:
        return f"{self.filename}:{self.line}:{self.column + 1} [{self.prefix}{self.code}]: {self.msg}"  # noqa: E501

    @classmethod
    def from_node(cls, node: Node, msg: str | None = None) -> Error:
        return cls(
            node.line,
            node.column,
            line_end=node.end_line,
            column_end=node.end_column,
            msg=msg or cls.msg,
        )
