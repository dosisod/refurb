from dataclasses import dataclass

from mypy.nodes import ArgKind, CallExpr, Decorator, NameExpr

from refurb.error import Error
from refurb.settings import Settings


@dataclass
class ErrorInfo(Error):
    """
    Python 3.9 introduces the `@cache` decorator which can be used as a
    short-hand for `@lru_cache(maxsize=None)`.

    Bad:

    ```
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def f(x: int) -> int:
        return x + 1
    ```

    Good:

    ```
    from functools import cache

    @cache
    def f(x: int) -> int:
        return x + 1
    ```
    """

    name = "use-cache"
    code = 134
    msg: str = "Replace `@lru_cache(maxsize=None)` with `@cache`"
    categories = ["functools", "readability"]


def check(node: Decorator, errors: list[Error], settings: Settings) -> None:
    if settings.python_version and settings.python_version < (3, 9):
        return  # pragma: no cover

    match node:
        case Decorator(
            decorators=[
                CallExpr(
                    callee=NameExpr(fullname="functools.lru_cache"),
                    arg_names=["maxsize"],
                    arg_kinds=[ArgKind.ARG_NAMED],
                    args=[NameExpr(fullname="builtins.None")],
                )
            ]
        ):
            errors.append(ErrorInfo(node.line, node.column))
