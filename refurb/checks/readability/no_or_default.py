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

from refurb.checks.common import extract_binary_oper, stringify
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
    categories = ("logical", "readability")


def check(node: OpExpr, errors: list[Error]) -> None:
    match extract_binary_oper("or", node):
        case (NameExpr(node=Var(type=ty)) as lhs, arg):
            match arg:
                case CallExpr(callee=NameExpr(fullname=fullname), args=[]):
                    pass

                case ListExpr(items=[]):
                    fullname = "builtins.list"

                case DictExpr(items=[]):
                    fullname = "builtins.dict"

                case TupleExpr(items=[]):
                    fullname = "builtins.tuple"

                case StrExpr(value=""):
                    fullname = "builtins.str"

                case BytesExpr(value=""):
                    fullname = "builtins.bytes"

                case IntExpr(value=0):
                    fullname = "builtins.int"

                case NameExpr(fullname="builtins.False"):
                    fullname = "builtins.bool"

                case _:
                    return

            type_name = "builtins.tuple" if str(ty).lower().startswith("tuple[") else str(ty)

            # Must check fullname for compatibility with older Mypy versions
            if fullname and type_name.startswith(fullname):
                lhs_expr = stringify(lhs)
                rhs_expr = stringify(arg)

                msg = f"Replace `{lhs_expr} or {rhs_expr}` with `{lhs_expr}`"

                errors.append(ErrorInfo.from_node(node, msg))
