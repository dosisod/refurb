from dataclasses import dataclass

from mypy.nodes import CallExpr, NameExpr, StrExpr

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    `print("")` can be simplified to just `print()`.
    """

    name = "simplify-print"
    code = 105
    msg: str = 'Replace `print("")` with `print()`'
    categories = ["builtin", "readability"]


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=NameExpr(fullname="builtins.print"),
            args=[StrExpr(value="")],
        ):
            errors.append(ErrorInfo(node.line, node.column))
