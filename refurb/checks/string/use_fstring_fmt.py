from dataclasses import dataclass

from mypy.nodes import CallExpr, MemberExpr, NameExpr, StrExpr

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
    categories = ["builtin", "fstring"]


CONVERSIONS = {
    "builtins.str": "x",
    "builtins.repr": "x!r",
    "builtins.ascii": "x!a",
    "builtins.bin": "x:#b",
    "builtins.oct": "x:#o",
    "builtins.hex": "x:#x",
    "builtins.chr": "x:c",
    "builtins.format": "x",
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
                    args=[_],
                ) if fullname in CONVERSIONS:
                    func_name = f"{{{func.name}(x)}}"
                    conversion = f"{{{CONVERSIONS[fullname or '']}}}"

                    errors.append(
                        ErrorInfo(
                            node.line,
                            node.column,
                            f"Replace `{func_name}` with `{conversion}`",
                        )
                    )
