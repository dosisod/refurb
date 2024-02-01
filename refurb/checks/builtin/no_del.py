from dataclasses import dataclass

from mypy.nodes import AssignmentStmt, DelStmt, IndexExpr, ListExpr, RefExpr, SliceExpr, Var

from refurb.checks.common import stringify
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Slice expressions can be used to replace part a list without reassigning
    it. If you want to clear all the elements out of a list while maintaining
    the same reference, don't use `del x[:]` or `x[:] = []`, use the faster
    `x.clear()` method instead.

    Bad:

    ```
    nums = [1, 2, 3]

    del nums[:]
    # or
    nums[:] = []
    ```

    Good:

    ```
    nums = [1, 2, 3]

    nums.clear()
    ```
    """

    name = "use-clear"
    code = 131
    categories = ("builtin", "readability")


def check(node: DelStmt | AssignmentStmt, errors: list[Error]) -> None:
    match node:
        case DelStmt(
            expr=IndexExpr(
                base=RefExpr(node=Var(type=ty)) as name,
                index=SliceExpr(begin_index=None, end_index=None, stride=None),
            ),
        ) if str(ty).startswith("builtins.list["):
            pass

        case AssignmentStmt(
            lvalues=[
                IndexExpr(
                    base=RefExpr(node=Var(type=ty)) as name,
                    index=SliceExpr(begin_index=None, end_index=None, stride=None),
                ),
            ],
            rvalue=ListExpr(items=[]),
        ) if str(ty).startswith("builtins.list["):
            pass

        case _:
            return

    msg = f"Replace `{stringify(node)}` with `{stringify(name)}.clear()`"

    errors.append(ErrorInfo.from_node(node, msg))
