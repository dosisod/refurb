from dataclasses import dataclass

from mypy.nodes import CallExpr, IndexExpr, IntExpr, NameExpr, SliceExpr

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    The `bin()`, `oct()`, and `hex()` functions return the string
    representation of a number but with a prefix attached. If you don't want
    the prefix, you might be tempted to just slice it off, but using an
    f-string will give you more flexibility:

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
    categories = ["builtin", "fstring"]


FUNC_CONVERSIONS = {
    "builtins.bin": "b",
    "builtins.oct": "o",
    "builtins.hex": "x",
}


def check(node: IndexExpr, errors: list[Error]) -> None:
    match node:
        case IndexExpr(
            base=CallExpr(callee=NameExpr() as name_node),
            index=SliceExpr(begin_index=IntExpr(value=2), end_index=None),
        ) if name_node.fullname in FUNC_CONVERSIONS:
            format = FUNC_CONVERSIONS[name_node.fullname or ""]
            fstring = f'f"{{num:{format}}}"'

            errors.append(
                ErrorInfo(
                    node.line,
                    node.column,
                    f"Replace `{name_node.name}(num)[2:]` with `{fstring}`",
                )
            )
