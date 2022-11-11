from dataclasses import dataclass
from itertools import combinations

from mypy.nodes import ComparisonExpr, Expression, OpExpr

from refurb.checks.common import extract_binary_oper, is_equivalent
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    When checking that multiple objects are equal to each other, don't use
    an `and` expression. Use a comparison chain instead, for example:

    Bad:

    ```
    if x == y and x == z:
        pass
    ```

    Good:

    ```
    if x == y == z:
        pass
    ```

    Note: if `x` depends on side-effects, then this check should be ignored.
    """

    code = 124
    msg: str = "Replace `x == y and x == z` with `x == y == z`"
    categories = ["logical", "readability"]


def has_common_expr(*exprs: Expression) -> bool:
    for lhs, rhs in combinations(exprs, 2):
        if is_equivalent(lhs, rhs):
            return True

    return False


def check(node: OpExpr, errors: list[Error]) -> None:
    match extract_binary_oper("and", node):
        case (
            ComparisonExpr(operators=["=="], operands=[a, b]),
            ComparisonExpr(operators=["=="], operands=[c, d]),
        ) if has_common_expr(a, b, c, d):
            errors.append(ErrorInfo(a.line, a.column))
