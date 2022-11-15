from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, NewType


@dataclass(frozen=True)
class ErrorCode:
    id: int
    prefix: str = "FURB"

    @classmethod
    def from_error(cls, err: type[Error]) -> ErrorCode:
        return ErrorCode(err.code, err.prefix)

    def __str__(self) -> str:
        return f"{self.prefix}{self.id}"


ErrorCategory = NewType("ErrorCategory", str)

ErrorClassifier = ErrorCategory | ErrorCode


@dataclass
class Error:
    enabled: ClassVar[bool] = True
    prefix: ClassVar[str] = "FURB"
    categories: ClassVar[list[str]] = []
    code: ClassVar[int]
    line: int
    column: int
    msg: str
    filename: str | None = None

    def __str__(self) -> str:
        return f"{self.filename}:{self.line}:{self.column + 1} [{self.prefix}{self.code}]: {self.msg}"  # noqa: E501
