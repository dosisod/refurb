from dataclasses import dataclass

from mypy.nodes import ComparisonExpr, ListExpr, OpExpr, SetExpr, TupleExpr

from refurb.checks.common import (
    extract_binary_oper,
    is_equivalent,
    is_false_literal,
    is_true_literal,
    stringify,
)
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Don't check if a value is `True` or `False` using `in`, use an
    `isinstance()` call.

    Bad:

    ```
    if value in {True, False}:
        pass
    ```

    Good:

    ```
    if isinstance(value, bool):
        pass
    ```
    """

    name = "use-isinstance-bool"
    code = 191
    categories = ("readability",)


def check(node: ComparisonExpr | OpExpr, errors: list[Error]) -> None:
    match node:
        case ComparisonExpr(
            operators=["in" | "not in" as op],
            operands=[
                lhs,
                SetExpr(items=[t, f]) | TupleExpr(items=[t, f]) | ListExpr(items=[t, f]),
            ],
        ) if (is_true_literal(t) and is_false_literal(f)) or (
            is_false_literal(t) and is_true_literal(f)
        ):
            old = stringify(node)
            new = f"isinstance({stringify(lhs)}, bool)"

            if op == "not in":
                new = f"not {new}"

            msg = f"Replace `{old}` with `{new}`"

            errors.append(ErrorInfo.from_node(node, msg))

        case OpExpr():
            match extract_binary_oper("or", node):
                case (
                    ComparisonExpr(operands=[lhs, t], operators=["is" | "==" as lhs_op]),
                    ComparisonExpr(operands=[rhs, f], operators=["is" | "==" as rhs_op]),
                ) if (
                    lhs_op == rhs_op
                    and is_equivalent(lhs, rhs)
                    and (
                        (is_true_literal(t) and is_false_literal(f))
                        or (is_false_literal(t) and is_true_literal(f))
                    )
                ):
                    old = stringify(node)
                    new = f"isinstance({stringify(lhs)}, bool)"

                    msg = f"Replace `{old}` with `{new}`"

                    errors.append(ErrorInfo.from_node(node, msg))
