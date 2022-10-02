from collections import Counter
from dataclasses import dataclass

from mypy.nodes import ComparisonExpr, Expression, OpExpr

from refurb.checks.common import extract_binary_oper
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
    msg: str = "Use `x == y == z` instead of `x == y and x == z`"


def has_common_expr(exprs: tuple[Expression, ...]) -> bool:
    count = Counter(str(x) for x in exprs).most_common(1)[0][1]

    return count > 1


def check(node: OpExpr, errors: list[Error]) -> None:
    exprs = extract_binary_oper("and", node)

    # TODO: remove when next mypy version is released
    if not exprs:
        return

    match exprs:
        case (
            ComparisonExpr(operators=["=="], operands=[a, b]),
            ComparisonExpr(operators=["=="], operands=[c, d]),
        ) if has_common_expr((a, b, c, d)):
            errors.append(ErrorInfo(a.line, a.column))
