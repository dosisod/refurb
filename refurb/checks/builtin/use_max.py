from dataclasses import dataclass

from mypy.nodes import ComparisonExpr, ConditionalExpr

from refurb.checks.common import is_equivalent
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Certain ternary expressions can be written more succinctly using the
    builtin `max()` function:

    Bad:

    ```
    score1 = 90
    score2 = 99

    highest_score = score1 if score1 > score2 else score2
    ```

    Good:

    ```
    score1 = 90
    score2 = 99

    highest_score = max(score1, score2)
    ```
    """

    name = "use-min-max"
    code = 136
    categories = ["builtin", "logical", "readability"]


FUNC_TABLE = {
    "<": "min",
    "<=": "min",
    ">": "max",
    ">=": "max",
}


def flip_comparison_oper(oper: str) -> str:
    return {
        "<": ">",
        "<=": ">=",
        ">": "<",
        ">=": "<=",
    }.get(oper, oper)


def check(node: ConditionalExpr, errors: list[Error]) -> None:
    match node:
        case ConditionalExpr(
            if_expr=if_expr,
            cond=ComparisonExpr(operators=[oper], operands=[lhs, rhs]),
            else_expr=else_expr,
        ):
            if (
                is_equivalent(if_expr, lhs)
                and is_equivalent(rhs, else_expr)
                and (func := FUNC_TABLE.get(oper))
            ):
                errors.append(
                    ErrorInfo(
                        node.line,
                        node.column,
                        f"Replace `x if x {oper} y else y` with `{func}(x, y)`",  # noqa: E501
                    )
                )

            if (
                is_equivalent(if_expr, rhs)
                and is_equivalent(lhs, else_expr)
                and (func := FUNC_TABLE.get(flip_comparison_oper(oper)))
            ):
                errors.append(
                    ErrorInfo(
                        node.line,
                        node.column,
                        f"Replace `x if y {oper} x else y` with `{func}(y, x)`",  # noqa: E501
                    )
                )
