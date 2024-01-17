from dataclasses import dataclass

from mypy.nodes import CallExpr, IndexExpr, IntExpr, NameExpr, SliceExpr

from refurb.checks.common import stringify
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    The `bin()`, `oct()`, and `hex()` functions return the string
    representation of a number but with a prefix attached. If you don't want
    the prefix, you might be tempted to just slice it off, but using an
    f-string will give you more flexibility and let you work with negative
    numbers:

    Bad:

    ```
    print(bin(1337)[2:])
    ```

    Good:

    ```
    print(f"{1337:b}")
    ```
    """

    name = "use-fstring-number-format"
    code = 116
    categories = ("builtin", "fstring")


FUNC_CONVERSIONS = {
    "builtins.bin": "b",
    "builtins.oct": "o",
    "builtins.hex": "x",
}


def check(node: IndexExpr, errors: list[Error]) -> None:
    match node:
        case IndexExpr(
            base=CallExpr(callee=NameExpr() as name_node, args=[arg]),
            index=SliceExpr(begin_index=IntExpr(value=2), end_index=None),
        ) if name_node.fullname in FUNC_CONVERSIONS:
            arg = stringify(arg)  # type: ignore

            format = FUNC_CONVERSIONS[name_node.fullname or ""]
            fstring = f'f"{{{arg}:{format}}}"'

            msg = f"Replace `{stringify(node)}` with `{fstring}`"

            errors.append(ErrorInfo.from_node(node, msg))
