from dataclasses import dataclass

from mypy.nodes import (
    CallExpr,
    ComparisonExpr,
    Expression,
    IndexExpr,
    OpExpr,
)
from refurb.visitor import TraverserVisitor

from refurb.checks.common import (
    extract_binary_oper,
    get_common_expr_in_comparison_chain,
    is_equivalent,
)
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    When comparing a value to multiple possible options, don't `or` multiple
    comparison checks, use a single `in` expr:

    Bad:

    ```
    if x == "abc" or x == "def":
        pass
    ```

    Good:

    ```
    if x in ("abc", "def"):
        pass
    ```

    Note: This should not be used if the operands depend on boolean short
    circuiting, since the operands will be eagerly evaluated. This is primarily
    useful for comparing against a range of constant values.
    """

    name = "use-in-oper"
    code = 108
    categories = ("logical", "readability")


def create_message(indices: tuple[int, int]) -> str:
    names = ["x", "y", "z"]
    common_name = names[indices[0]]
    names.insert(indices[1], common_name)

    old = f"{names[0]} == {names[1]} or {names[2]} == {names[3]}"

    names = [name for name in names if name != common_name]
    new = f"{common_name} in ({', '.join(names)})"

    return f"Replace `{old}` with `{new}`"


class _HasComplexExprVisitor(TraverserVisitor):
    """Check if an expression contains sub-expressions that could
    raise or have side effects (subscripts, calls, etc.)."""

    found: bool = False

    def visit_index_expr(self, node: IndexExpr) -> None:
        self.found = True

    def visit_call_expr(self, node: CallExpr) -> None:
        self.found = True


def _has_complex_operands(node: OpExpr) -> bool:
    """Return True if the non-common operands in an or-comparison
    contain expressions that may depend on short-circuit evaluation."""
    match extract_binary_oper("or", node):
        case (
            ComparisonExpr(operators=["=="], operands=[a, b]),
            ComparisonExpr(operators=["=="], operands=[c, d]),
        ):
            # Find which operands are common (shared between both sides)
            non_common: list[Expression] = []
            if is_equivalent(a, c) or is_equivalent(a, d):
                non_common.append(b)
                non_common.append(d if is_equivalent(a, c) else c)
            elif is_equivalent(b, c) or is_equivalent(b, d):
                non_common.append(a)
                non_common.append(d if is_equivalent(b, c) else c)
            else:
                return False

            for operand in non_common:
                visitor = _HasComplexExprVisitor()
                visitor.accept(operand)
                if visitor.found:
                    return True

    return False


def check(node: OpExpr, errors: list[Error]) -> None:
    if data := get_common_expr_in_comparison_chain(node, oper="or"):
        if _has_complex_operands(node):
            return

        expr, indices = data

        errors.append(ErrorInfo.from_node(expr, create_message(indices)))
