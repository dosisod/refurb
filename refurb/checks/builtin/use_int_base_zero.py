from dataclasses import dataclass

from mypy.nodes import (
    ArgKind,
    CallExpr,
    IndexExpr,
    IntExpr,
    RefExpr,
    SliceExpr,
)

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    When converting a string starting with `0b`, `0o`, or `0x` to an int, you
    don't need to slice the string and set the base yourself: just call `int()`
    with a base of zero. Doing this will autodeduce the correct base to use
    based on the string prefix.

    Bad:

    ```
    num = "0xABC"

    if num.startswith("0b"):
        i = int(num[2:], 2)
    elif num.startswith("0o"):
        i = int(num[2:], 8)
    elif num.startswith("0x"):
        i = int(num[2:], 16)

    print(i)
    ```

    Good:

    ```
    num = "0xABC"

    i = int(num, 0)

    print(i)
    ```

    This check is disabled by default because there is no way for Refurb to
    detect whether the prefixes that are being stripped are valid Python int
    prefixes (like `0x`) or some other prefix which would fail if parsed using
    this method.
    """

    enabled = False
    name = "use-int-base-zero"
    code = 166
    categories = ("builtin", "readability")


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=RefExpr(fullname="builtins.int"),
            args=[
                IndexExpr(
                    index=SliceExpr(
                        begin_index=IntExpr(value=2),
                        end_index=None,
                        stride=None,
                    ),
                ),
                IntExpr(value=2 | 8 | 16 as base),
            ],
            arg_kinds=arg_kinds,
            arg_names=[_, "base" | None],
        ):
            kw = "base=" if arg_kinds[1] == ArgKind.ARG_NAMED else ""

            errors.append(
                ErrorInfo.from_node(
                    node,
                    f"Replace `int(x[2:], {kw}{base})` with `int(x, {kw}0)`",
                )
            )
