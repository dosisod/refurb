from mypy.nodes import ComparisonExpr, ListExpr

from refurb.error import Error

from .error import ErrorUseTupleWithInExpr


def check(node: ComparisonExpr, errors: list[Error]) -> None:
    match node:
        case ComparisonExpr(
            operators=["in"],
            operands=[_, ListExpr() as expr],
        ):
            errors.append(ErrorUseTupleWithInExpr(expr.line, expr.column))
