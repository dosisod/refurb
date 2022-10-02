from dataclasses import dataclass

from mypy.nodes import (
    BytesExpr,
    CallExpr,
    IntExpr,
    MemberExpr,
    NameExpr,
    OpExpr,
    StrExpr,
)

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Instead of using `replace("\\t", " " * 8)`, you can use the `expandtabs()`
    method. It is more succinct and descriptive. It also allows for an optional
    parameter for specifying the tab width.

    Bad:

    ```
    spaces_8 = "hello\\tworld".replace("\\t", " " * 8)
    spaces_4 = "hello\\tworld".replace("\\t", "    ")
    ```

    Good:

    ```
    spaces_8 = "hello\\tworld".expandtabs()
    spaces_4 = "hello\\tworld".expandtabs(4)
    ```
    """

    code = 106


def check_str(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=MemberExpr(name="replace") as func,
            args=[StrExpr(value="\t"), replace],
        ):
            match replace:
                case StrExpr(value=s) if all(c == " " for c in s):
                    tabsize = str(len(s))
                    expr_value = f'"{s}"'

                case OpExpr(
                    op="*",
                    left=StrExpr(value=" "),
                    right=IntExpr(value=value) | NameExpr(name=value),
                ):
                    tabsize = str(value)
                    expr_value = f'" " * {value}'

                case _:
                    return

            if tabsize == "8":
                tabsize = ""

            errors.append(
                ErrorInfo(
                    func.line,
                    (func.end_column or 0) - len("replace"),
                    f'Replace `x.replace("\\t", {expr_value})` with `x.expandtabs({tabsize})`',  # noqa: E501
                )
            )


def check_bytes(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=MemberExpr(name="replace") as func,
            args=[BytesExpr(value="\\t"), replace],
        ):
            match replace:
                case BytesExpr(value=s) if all(c == " " for c in s):
                    tabsize = str(len(s))
                    expr_value = f'b"{s}"'

                case OpExpr(
                    op="*",
                    left=BytesExpr(value=" "),
                    right=IntExpr(value=value) | NameExpr(name=value),
                ):
                    tabsize = str(value)
                    expr_value = f'b" " * {value}'

                case _:
                    return

            if tabsize == "8":
                tabsize = ""

            errors.append(
                ErrorInfo(
                    func.line,
                    (func.end_column or 0) - len("replace"),
                    f'Replace `x.replace(b"\\t", {expr_value})` with `x.expandtabs({tabsize})`',  # noqa: E501
                )
            )


def check(node: CallExpr, errors: list[Error]) -> None:
    check_str(node, errors)
    check_bytes(node, errors)
