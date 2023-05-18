from dataclasses import dataclass

from mypy.nodes import (
    CallExpr,
    IndexExpr,
    IntExpr,
    MemberExpr,
    NameExpr,
    RefExpr,
    SliceExpr,
    StrExpr,
)

from refurb.error import Error
from refurb.settings import Settings


@dataclass
class ErrorInfo(Error):
    """
    Python 3.10 adds a very helpful `bit_count()` function for integers which
    counts the number of set bits. This new function is more descriptive and
    faster compared to converting/counting characters in a string.

    Bad:

    ```
    x = bin(0b1010).count("1")

    assert x == 2
    ```

    Good:

    ```
    x = 0b1010.bit_count()

    assert x == 2
    ```
    """

    name = "use-bit-count"
    code = 161
    categories = ("builtin", "performance", "python310", "readability")


def check(node: CallExpr, errors: list[Error], settings: Settings) -> None:
    if settings.get_python_version() < (3, 10):
        return  # pragma: no cover

    match node:
        case CallExpr(
            callee=MemberExpr(
                expr=IndexExpr(
                    base=bin_func,
                    index=SliceExpr(
                        begin_index=IntExpr(value=2),
                        end_index=None,
                        stride=None,
                    ),
                )
                | bin_func,
                name="count",
            ),
            args=[StrExpr(value="1")],
        ):
            match bin_func:
                case CallExpr(
                    callee=NameExpr(fullname="builtins.bin"),
                    args=[arg],
                ):
                    pass

                case _:
                    return

            if isinstance(node.callee.expr, IndexExpr):  # type: ignore
                old = "bin(x)[2:]"
            else:
                old = "bin(x)"

            if isinstance(arg, IntExpr | RefExpr | CallExpr | IndexExpr):
                x = "x"
            else:
                x = "(x)"

            errors.append(
                ErrorInfo.from_node(
                    node, f'Replace `{old}.count("1")` with `{x}.bit_count()`'
                )
            )
