from dataclasses import dataclass

from mypy.nodes import (
    AssignmentStmt,
    CallExpr,
    IndexExpr,
    IntExpr,
    NameExpr,
    SliceExpr,
    UnaryExpr,
    Var,
)

from refurb.checks.common import stringify, unmangle_name
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Don't use `x[::-1]` or `reversed(x)` to reverse a list and reassign it to
    itself, use the faster in-place `.reverse()` method instead.

    Bad:

    ```
    names = ["Bob", "Alice", "Charlie"]

    names = reverse(names)
    # or
    names = list(reverse(names))
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
            lvalues=[NameExpr(fullname=assign_name) as assign_ref],
            rvalue=CallExpr(
                callee=NameExpr(fullname="builtins.reversed"),
                args=[NameExpr(fullname=reverse_name, node=Var(type=ty))],
            ),
        ) if (
            unmangle_name(assign_name) == unmangle_name(reverse_name)
            and str(ty).startswith("builtins.list[")
        ):
            pass

        case AssignmentStmt(
            lvalues=[NameExpr(fullname=assign_name) as assign_ref],
            rvalue=CallExpr(
                callee=NameExpr(fullname="builtins.list"),
                args=[
                    CallExpr(
                        callee=NameExpr(fullname="builtins.reversed"),
                        args=[NameExpr(fullname=reverse_name, node=Var(type=ty))],
                    ),
                ],
            ),
        ) if (
            unmangle_name(assign_name) == unmangle_name(reverse_name)
            and str(ty).startswith("builtins.list[")
        ):
            pass

        case AssignmentStmt(
            lvalues=[NameExpr(fullname=assign_name) as assign_ref],
            rvalue=IndexExpr(
                base=NameExpr(fullname=reverse_name, node=Var(type=ty)),
                index=SliceExpr(
                    begin_index=None,
                    end_index=None,
                    stride=UnaryExpr(op="-", expr=IntExpr(value=1)),
                ),
            ),
        ) if (
            unmangle_name(assign_name) == unmangle_name(reverse_name)
            and str(ty).startswith("builtins.list[")
        ):
            pass

        case _:
            return

    old = stringify(node)
    new = f"{stringify(assign_ref)}.reverse()"

    msg = f"Replace `{old}` with `{new}`"

    errors.append(ErrorInfo.from_node(node, msg))
