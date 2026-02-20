from dataclasses import dataclass

from mypy.nodes import (
    BytesExpr,
    CallExpr,
    ComparisonExpr,
    ComplexExpr,
    Expression,
    FloatExpr,
    IndexExpr,
    IntExpr,
    MemberExpr,
    NameExpr,
    OpExpr,
    StrExpr,
    UnaryExpr,
)

from refurb.checks.common import (
    extract_binary_oper,
    get_common_expr_in_comparison_chain,
    get_common_expr_positions,
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


def _is_simple_expr(node: Expression) -> bool:
    """
    Check if an expression is simple enough to be safely eagerly evaluated.

    Simple expressions are those that cannot raise exceptions or have side
    effects when evaluated, making them safe for use in `in` tuple checks
    where short-circuit evaluation is lost.
    """
    match node:
        case NameExpr() | IntExpr() | StrExpr() | BytesExpr() | FloatExpr() | ComplexExpr():
            return True

        case MemberExpr(expr=expr):
            return _is_simple_expr(expr)

        case UnaryExpr(expr=expr):
            return _is_simple_expr(expr)

        case OpExpr(left=left, right=right):
            return _is_simple_expr(left) and _is_simple_expr(right)

        case IndexExpr() | CallExpr():
            return False

    return False


def _get_non_common_operands(node: OpExpr) -> list[Expression] | None:
    """
    Extract non-common operands from a comparison chain.

    Given `a == b or c == d` where some operands are common,
    returns the non-common operands (those that would be eagerly
    evaluated in an `in` tuple).
    """
    match extract_binary_oper("or", node):
        case (
            ComparisonExpr(operators=[lhs_oper], operands=[a, b]),
            ComparisonExpr(operators=[rhs_oper], operands=[c, d]),
        ) if lhs_oper == rhs_oper == "==" and (indices := get_common_expr_positions(a, b, c, d)):
            operands = [a, b, c, d]
            return [op for i, op in enumerate(operands) if i not in indices]

    return None


def create_message(indices: tuple[int, int]) -> str:
    names = ["x", "y", "z"]
    common_name = names[indices[0]]
    names.insert(indices[1], common_name)

    old = f"{names[0]} == {names[1]} or {names[2]} == {names[3]}"

    names = [name for name in names if name != common_name]
    new = f"{common_name} in ({', '.join(names)})"

    return f"Replace `{old}` with `{new}`"


def check(node: OpExpr, errors: list[Error]) -> None:
    if data := get_common_expr_in_comparison_chain(node, oper="or"):
        expr, indices = data

        non_common = _get_non_common_operands(node)
        if non_common is not None and not all(_is_simple_expr(op) for op in non_common):
            return

        errors.append(ErrorInfo.from_node(expr, create_message(indices)))
