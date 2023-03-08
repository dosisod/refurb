from __future__ import annotations

from pathlib import Path

# these should match

_ = Path().cwd()
_ = Path("filename").cwd()

class C:
    @staticmethod
    def s(*args: str) -> None:
        pass

    @classmethod
    def c(cls, *args: str) -> C:
        return cls()

    def f(self) -> None:
        return

C().s()
C().c()
C().s("hello", "world")
C().c("hello", "world")

# these should not

_ = Path.cwd()

C().f()
