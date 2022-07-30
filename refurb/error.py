from dataclasses import dataclass
from typing import Optional


@dataclass
class Error:
    code: int
    line: int
    column: int
    msg: str
    filename: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.filename}:{self.line}:{self.column} [FURB{self.code}]: {self.msg}"  # noqa
