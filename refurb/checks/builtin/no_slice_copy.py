from dataclasses import dataclass

from mypy.nodes import AssignmentStmt, DelStmt, IndexExpr, MypyFile, RefExpr, SliceExpr, Var

from refurb.checks.common import stringify
from refurb.error import Error
from refurb.visitor import TraverserVisitor


@dataclass
class ErrorInfo(Error):
    """
    Don't use a slice expression (with no bounds) to make a copy of something,
    use the more readable `.copy()` method instead:

    Bad:

    ```
    nums = [3.1415, 1234]
    copy = nums[:]
    ```

    Good:

    ```
    nums = [3.1415, 1234]
    copy = nums.copy()
    ```
    """

    name = "no-slice-copy"
    code = 145
    categories = ("readability",)


SEQUENCE_BUILTINS = (
    "builtins.bytearray",
    "builtins.list[",
    "builtins.tuple[",
    "tuple[",
)


class SliceExprVisitor(TraverserVisitor):
    errors: list[Error]

    def __init__(self, errors: list[Error]) -> None:
        super().__init__()

        self.errors = errors

    def visit_assignment_stmt(self, node: AssignmentStmt) -> None:
        self.accept(node.rvalue)

    def visit_del_stmt(self, node: DelStmt) -> None:
        if not isinstance(node.expr, IndexExpr):
            self.accept(node.expr)

    def visit_index_expr(self, node: IndexExpr) -> None:
        match node.base:
            case RefExpr(node=Var(type=ty)):
                if not str(ty).startswith(SEQUENCE_BUILTINS):
                    return

            case _:
                return

        match node.index:
            case SliceExpr(begin_index=None, end_index=None, stride=None):
                base = stringify(node.base)
                msg = f"Replace `{base}[:]` with `{base}.copy()`"

                self.errors.append(ErrorInfo.from_node(node, msg))


def check(node: MypyFile, errors: list[Error]) -> None:
    SliceExprVisitor(errors).accept(node)
