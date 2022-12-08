from dataclasses import dataclass

from mypy.nodes import AssignmentStmt, MypyFile, SliceExpr
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

    def visit_slice_expr(self, node: SliceExpr) -> None:
        if node.begin_index is node.end_index is node.stride is None:
            self.errors.append(ErrorInfo(node.line, node.column))


def check(node: MypyFile, errors: list[Error]) -> None:
    node.accept(SliceExprVisitor(errors))
