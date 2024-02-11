from dataclasses import dataclass

from mypy.nodes import AssignmentStmt, CallExpr, IndexExpr, IntExpr, NameExpr, SliceExpr, UnaryExpr

from refurb.checks.common import get_mypy_type, is_equivalent, is_same_type, stringify
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Don't use `x[::-1]` or `reversed(x)` to reverse a list and reassign it to
    itself, use the faster in-place `.reverse()` method instead.

    Bad:

    ```
    names = ["Bob", "Alice", "Charlie"]

    names = reversed(names)
    # or
    names = list(reversed(names))
    # or
    names = names[::-1]
    ```

    Good:

    ```
    names = ["Bob", "Alice", "Charlie"]

    names.reverse()
    ```
    """

    name = "use-reverse"
    categories = ("performance", "readability")
    code = 187


def check(node: AssignmentStmt, errors: list[Error]) -> None:
    match node:
        case AssignmentStmt(
            lvalues=[assign_ref],
            rvalue=CallExpr(
                callee=NameExpr(fullname="builtins.reversed"),
                args=[reverse_expr],
            ),
        ):
            pass

        case AssignmentStmt(
            lvalues=[assign_ref],
            rvalue=CallExpr(
                callee=NameExpr(fullname="builtins.list"),
                args=[
                    CallExpr(
                        callee=NameExpr(fullname="builtins.reversed"),
                        args=[reverse_expr],
                    ),
                ],
            ),
        ):
            pass

        case AssignmentStmt(
            lvalues=[assign_ref],
            rvalue=IndexExpr(
                base=reverse_expr,
                index=SliceExpr(
                    begin_index=None,
                    end_index=None,
                    stride=UnaryExpr(op="-", expr=IntExpr(value=1)),
                ),
            ),
        ):
            pass

        case _:
            return

    if is_equivalent(assign_ref, reverse_expr) and is_same_type(get_mypy_type(reverse_expr), list):
        old = stringify(node)
        new = f"{stringify(assign_ref)}.reverse()"

        msg = f"Replace `{old}` with `{new}`"

        errors.append(ErrorInfo.from_node(node, msg))
