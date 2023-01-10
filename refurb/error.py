from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar


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
    categories: ClassVar[list[str]] = []
    code: ClassVar[int]
    line: int
    column: int
    msg: str
    filename: str | None = None

    def __str__(self) -> str:
        return f"{self.filename}:{self.line}:{self.column + 1} [{self.prefix}{self.code}]: {self.msg}"  # noqa: E501
