from dataclasses import dataclass

from mypy.nodes import CallExpr, ListExpr, MemberExpr, NameExpr, StrExpr

from refurb.checks.common import stringify
from refurb.checks.string.use_fstring_fmt import CONVERSIONS as FURB_119_FUNCS
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    If you want to stringify a single value without concatenating anything, use
    the `str()` function instead.

    Bad:

    ```
    nums = [123, 456]
    num = f"{num[0]}")
    ```

    Good:

    ```
    nums = [123, 456]
    num = str(num[0])
    ```
    """

    name = "use-str-func"
    code = 183
    categories = ("readability",)


ignore = set[int]()


def check(node: CallExpr, errors: list[Error]) -> None:
    if id(node) in ignore:
        return

    match node:
        case CallExpr(
            callee=MemberExpr(
                expr=StrExpr(value=""),
                name="join",
            ),
            args=[ListExpr(items=items)],
        ):
            ignore.update(id(item) for item in items)

        case CallExpr(
            callee=MemberExpr(
                expr=StrExpr(value="{:{}}"),
                name="format",
            ),
            args=[arg, StrExpr(value="")],
        ):
            match arg:
                case CallExpr(callee=NameExpr(fullname=fn)) if fn in FURB_119_FUNCS:
                    return

            x = stringify(arg)

            msg = f'Replace `f"{{{x}}}"` with `str({x})`'

            errors.append(ErrorInfo.from_node(node, msg))
