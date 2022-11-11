from dataclasses import dataclass

from mypy.nodes import ComparisonExpr, OpExpr

from refurb.checks.common import extract_binary_oper, is_equivalent
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
    msg: str = "Replace `x == y or x == z` with `x in (y, z)`"
    categories = ["logical", "readability"]


def check(node: OpExpr, errors: list[Error]) -> None:
    match extract_binary_oper("or", node):
        case (
            ComparisonExpr(operators=["=="], operands=[lhs, _]),
            ComparisonExpr(operators=["=="], operands=[rhs, _]),
        ) if is_equivalent(lhs, rhs):
            errors.append(ErrorInfo(lhs.line, lhs.column))
