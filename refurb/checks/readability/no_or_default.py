from dataclasses import dataclass

from mypy.nodes import (
    BytesExpr,
    CallExpr,
    DictExpr,
    IntExpr,
    ListExpr,
    NameExpr,
    OpExpr,
    StrExpr,
    TupleExpr,
    Var,
)

from refurb.checks.common import extract_binary_oper
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Don't check an expression to see if it is falsey then assign the same
    falsey value to it. For example, if an expression used to be of type
    `int | None`, checking if the expression is falsey would make sense,
    since it could be `None` or `0`. But, if the expression is changed to
    be of type `int`, the falsey value is just `0`, so setting it to `0`
    if it is falsey (`0`) is redundant.

    Bad:

    ```
    def is_markdown_header(line: str) -> bool:
        return (line or "").startswith("#")
    ```

    Good:

    ```
    def is_markdown_header(line: str) -> bool:
        return line.startswith("#")
    ```
    """

    name = "no-default-or"
    code = 143
    categories = ["logical", "readability"]


def check(node: OpExpr, errors: list[Error]) -> None:
    match extract_binary_oper("or", node):
        case (NameExpr(node=Var(type=ty)), arg):
            match arg:
                case CallExpr(
                    callee=NameExpr(name=name, fullname=fullname), args=[]
                ):
                    fullname = fullname
                    expr = f"{name}()"

                case ListExpr(items=[]):
                    fullname = "builtins.list"
                    expr = "[]"

                case DictExpr(items=[]):
                    fullname = "builtins.dict"
                    expr = "{}"

                case TupleExpr(items=[]):
                    fullname = "builtins.tuple"
                    expr = "()"

                case StrExpr(value=""):
                    fullname = "builtins.str"
                    expr = '""'

                case BytesExpr(value=""):
                    fullname = "builtins.bytes"
                    expr = 'b""'

                case IntExpr(value=0):
                    fullname = "builtins.int"
                    expr = "0"

                case NameExpr(fullname="builtins.False"):
                    fullname = "builtins.bool"
                    expr = "False"

                case _:
                    return

            type_name = "builtins.tuple" if str(ty) == "Tuple[]" else str(ty)

            if fullname and type_name.startswith(fullname):
                errors.append(
                    ErrorInfo(
                        node.line,
                        node.column,
                        f"Replace `x or {expr}` with `x`",
                    )
                )
