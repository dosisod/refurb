from dataclasses import dataclass

from mypy.nodes import AssignmentStmt, DelStmt, IndexExpr, MypyFile, SliceExpr
from mypy.traverser import TraverserVisitor

from refurb.error import Error


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
    msg: str = "Replace `x[:]` with `x.copy()`"
    categories = ["readability"]


class SliceExprVisitor(TraverserVisitor):
    errors: list[Error]

    def __init__(self, errors: list[Error]) -> None:
        super().__init__()

        self.errors = errors

    def visit_assignment_stmt(self, node: AssignmentStmt) -> None:
        node.rvalue.accept(self)

    def visit_del_stmt(self, node: DelStmt) -> None:
        if not isinstance(node.expr, IndexExpr):
            node.expr.accept(self)

    def visit_index_expr(self, node: IndexExpr) -> None:
        index = node.index

        if (
            isinstance(index, SliceExpr)
            and index.begin_index is index.end_index is index.stride is None
        ):
            self.errors.append(ErrorInfo(node.line, node.column))


def check(node: MypyFile, errors: list[Error]) -> None:
    node.accept(SliceExprVisitor(errors))
