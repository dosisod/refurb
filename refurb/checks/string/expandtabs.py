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
    If you want to expand the tabs at the start of a string, don't use
    `.replace("\\t", " " * 8)`, use `.expandtabs()` instead. Note that this
    only works if the tabs are at the start of the string, since `expandtabs()`
    will expand each tab to the nearest tab column.

    Bad:

    ```
    spaces_8 = "\\thello world".replace("\\t", " " * 8)
    spaces_4 = "\\thello world".replace("\\t", "    ")
    ```

    Good:

    ```
    spaces_8 = "\\thello world".expandtabs()
    spaces_4 = "\\thello world".expandtabs(4)
    ```
    """

    name = "use-expandtabs"
    enabled = False
    code = 106
    categories = ["string"]


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

                case OpExpr(
                    op="*",
                    left=IntExpr(value=value) | NameExpr(name=value),
                    right=StrExpr(value=" "),
                ):
                    tabsize = str(value)
                    expr_value = f'{value} * " "'

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

                case OpExpr(
                    op="*",
                    left=IntExpr(value=value) | NameExpr(name=value),
                    right=BytesExpr(value=" "),
                ):
                    tabsize = str(value)
                    expr_value = f'{value} * b" "'

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
