from dataclasses import dataclass

from mypy.nodes import CallExpr, MemberExpr, NameExpr, StrExpr

from refurb.checks.common import stringify
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Certain expressions which are passed to f-strings are redundant because
    the f-string itself is capable of formatting it. For example:

    Bad:

    ```
    print(f"{bin(1337)}")

    print(f"{ascii(input())}")

    print(f"{str(123)}")
    ```

    Good:

    ```
    print(f"{1337:#b}")

    print(f"{input()!a}")

    print(f"{123}")
    ```
    """

    name = "use-fstring-format"
    code = 119
    categories = ("builtin", "fstring")


CONVERSIONS = {
    "builtins.str": "",
    "builtins.repr": "!r",
    "builtins.ascii": "!a",
    "builtins.bin": ":#b",
    "builtins.oct": ":#o",
    "builtins.hex": ":#x",
    "builtins.chr": ":c",
    "builtins.format": "",
}


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=MemberExpr(expr=StrExpr(value="{:{}}"), name="format"),
            args=[inner, _],
        ):
            match inner:
                case CallExpr(
                    callee=NameExpr(fullname=fullname) as func,
                    args=[arg],
                ) if fullname in CONVERSIONS:
                    arg = stringify(arg)  # type: ignore

                    func_name = f"{{{func.name}({arg})}}"
                    conversion = f"{{{arg}{CONVERSIONS[fullname or '']}}}"  # noqa: FURB143

                    errors.append(
                        ErrorInfo.from_node(node, f"Replace `{func_name}` with `{conversion}`")
                    )
