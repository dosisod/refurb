from collections.abc import Callable
from itertools import combinations

from mypy.nodes import (
    Block,
    ComparisonExpr,
    Expression,
    MemberExpr,
    MypyFile,
    NameExpr,
    Node,
    OpExpr,
    Statement,
)

from refurb.error import Error


def extract_binary_oper(
    oper: str, node: OpExpr
) -> tuple[Expression, Expression] | None:
    match node:
        case OpExpr(
            op=op,
            left=lhs,
            right=rhs,
        ) if op == oper:
            match rhs:
                case OpExpr(op=op, left=rhs) if op == oper:
                    return lhs, rhs

                case OpExpr():
                    return None

                case Expression():
                    return lhs, rhs

    return None


def check_block_like(
    func: Callable[[list[Statement], list[Error]], None],
    node: Block | MypyFile,
    errors: list[Error],
) -> None:
    match node:
        case Block():
            func(node.body, errors)

        case MypyFile():
            func(node.defs, errors)


def unmangle_name(name: str | None) -> str:
    return (name or "").replace("'", "")


def is_equivalent(lhs: Node, rhs: Node) -> bool:
    match (lhs, rhs):
        case NameExpr() as lhs, NameExpr() as rhs:
            return unmangle_name(lhs.fullname) == unmangle_name(rhs.fullname)

        case MemberExpr() as lhs, MemberExpr() as rhs:
            return (
                lhs.name == rhs.name
                and unmangle_name(lhs.fullname) == unmangle_name(rhs.fullname)
                and is_equivalent(lhs.expr, rhs.expr)
            )

    return str(lhs) == str(rhs)


def get_common_expr_positions(*exprs: Expression) -> tuple[int, int] | None:
    for lhs, rhs in combinations(exprs, 2):
        if is_equivalent(lhs, rhs):
            return exprs.index(lhs), exprs.index(rhs)

    return None


def get_common_expr_in_comparison_chain(
    node: OpExpr, oper: str
) -> tuple[Expression, tuple[int, int]] | None:
    """
    This function finds the first expression shared between 2 comparison
    expressions in the binary operator `oper`.

    For example, an OpExpr that looks like the following:

    1 == 2 or 3 == 1

    Will return a tuple containing the first common expression (`IntExpr(1)` in
    this case), and the indices of the common expressions as they appear in the
    source (`0` and `3` in this case). The indices are to be used for display
    purposes by the caller.

    If the binary operator is not composed of 2 comparison operators, or if
    there are no common expressions, `None` is returned.
    """

    match extract_binary_oper(oper, node):
        case (
            ComparisonExpr(operators=["=="], operands=[a, b]),
            ComparisonExpr(operators=["=="], operands=[c, d]),
        ) if indices := get_common_expr_positions(a, b, c, d):
            return a, indices
