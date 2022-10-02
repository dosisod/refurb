from dataclasses import dataclass

from mypy.nodes import ComparisonExpr, OpExpr

from refurb.checks.common import extract_binary_oper
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    When comparing a value to multiple possible options, don't use multiple
    `or` checks, use a single `in` expr:

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

    code = 108
    msg: str = "Use `x in (y, z)` instead of `x == y or x == z`"


def check(node: OpExpr, errors: list[Error]) -> None:
    exprs = extract_binary_oper("or", node)

    # TODO: remove when next mypy version is released
    if not exprs:
        return

    match exprs:
        case (
            ComparisonExpr(operators=["=="], operands=[lhs, _]),
            ComparisonExpr(operators=["=="], operands=[rhs, _]),
        ) if str(lhs) == str(rhs):
            errors.append(ErrorInfo(lhs.line, lhs.column))
