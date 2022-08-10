from mypy.nodes import GeneratorExpr, ListExpr

from refurb.error import Error

from .error import ErrorUseTupleWithInExpr


def check(node: GeneratorExpr, errors: list[Error]) -> None:
    for expr in node.sequences:
        if isinstance(expr, ListExpr):
            errors.append(ErrorUseTupleWithInExpr(expr.line, expr.column))
