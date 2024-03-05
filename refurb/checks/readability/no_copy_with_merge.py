from dataclasses import dataclass

from mypy.nodes import CallExpr, Expression, MemberExpr, OpExpr

from refurb.checks.common import get_mypy_type, is_same_type, stringify
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    You don't need to call `.copy()` on a dict/set when using it in a union
    since the original dict/set is not modified.

    Bad:

    ```
    d = {"a": 1}

    merged = d.copy() | {"b": 2}
    ```

    Good:

    ```
    d = {"a": 1}

    merged = d | {"b": 2}
    ```
    """

    name = "no-copy-with-merge"
    categories = ("readability",)
    code = 185


ignored_nodes = set[int]()


def check_expr(expr: Expression, errors: list[Error]) -> None:
    if id(expr) in ignored_nodes:
        return

    match expr:
        case CallExpr(
            callee=MemberExpr(expr=lhs, name="copy"),
            args=[],
        ) if is_same_type(get_mypy_type(lhs), dict, set, "os._Environ"):
            msg = f"Replace `{stringify(lhs)}.copy()` with `{stringify(lhs)}`"

            errors.append(ErrorInfo.from_node(expr, msg))

        case OpExpr(left=lhs, op="|", right=rhs):
            check_expr(lhs, errors)
            check_expr(rhs, errors)

            ignored_nodes.add(id(expr))


def check(node: OpExpr, errors: list[Error]) -> None:
    check_expr(node, errors)
