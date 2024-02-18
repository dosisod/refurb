from dataclasses import dataclass

from mypy.nodes import (
    BytesExpr,
    CallExpr,
    DictExpr,
    FloatExpr,
    IntExpr,
    ListExpr,
    NameExpr,
    OpExpr,
    StrExpr,
    TupleExpr,
)

from refurb.checks.common import (
    extract_binary_oper,
    get_mypy_type,
    is_same_type,
    mypy_type_to_python_type,
    stringify,
)
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
        case (
            lhs,
            (
                CallExpr(callee=NameExpr(fullname="builtins.set" | "builtins.frozenset"), args=[])
                | ListExpr(items=[])
                | DictExpr(items=[])
                | TupleExpr(items=[])
                | StrExpr(value="")
                | BytesExpr(value="")
                | IntExpr(value=0)
                | FloatExpr(value=0.0)
                | NameExpr(fullname="builtins.False")
            ) as rhs,
        ) if (expected_type := mypy_type_to_python_type(get_mypy_type(rhs))) and is_same_type(
            get_mypy_type(lhs), expected_type
        ):
            lhs_expr = stringify(lhs)

            msg = f"Replace `{lhs_expr} or {stringify(rhs)}` with `{lhs_expr}`"

            errors.append(ErrorInfo.from_node(node, msg))
