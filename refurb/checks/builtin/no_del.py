from dataclasses import dataclass

from mypy.nodes import AssignmentStmt, DelStmt, IndexExpr, ListExpr, SliceExpr

from refurb.checks.common import get_mypy_type, is_same_type, stringify
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
                base=base,
                index=SliceExpr(begin_index=None, end_index=None, stride=None),
            ),
        ):
            pass

        case AssignmentStmt(
            lvalues=[
                IndexExpr(
                    base=base,
                    index=SliceExpr(begin_index=None, end_index=None, stride=None),
                ),
            ],
            rvalue=ListExpr(items=[]),
        ):
            pass

        case _:
            return

    if is_same_type(get_mypy_type(base), list):
        msg = f"Replace `{stringify(node)}` with `{stringify(base)}.clear()`"

        errors.append(ErrorInfo.from_node(node, msg))
