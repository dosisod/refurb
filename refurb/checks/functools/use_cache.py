from dataclasses import dataclass

from mypy.nodes import ArgKind, CallExpr, Decorator, MemberExpr, RefExpr

from refurb.checks.common import is_none_literal
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
    categories = ("functools", "python39", "readability")


def check(node: Decorator, errors: list[Error], settings: Settings) -> None:
    if settings.get_python_version() < (3, 9):
        return  # pragma: no cover

    match node:
        case Decorator(
            decorators=[
                CallExpr(
                    callee=RefExpr(fullname="functools.lru_cache") as ref,
                    arg_names=["maxsize"],
                    arg_kinds=[ArgKind.ARG_NAMED],
                    args=[arg],
                )
            ]
        ) if is_none_literal(arg):
            prefix = "functools." if isinstance(ref, MemberExpr) else ""
            old = f"@{prefix}lru_cache(maxsize=None)"
            new = f"@{prefix}cache"

            msg = f"Replace `{old}` with `{new}`"

            errors.append(ErrorInfo.from_node(node, msg))
