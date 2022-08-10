from mypy.nodes import ForStmt, ListExpr

from refurb.error import Error

from .error import ErrorUseTupleWithInExpr


def check(node: ForStmt, errors: list[Error]) -> None:
    match node:
        case ForStmt(expr=ListExpr() as expr):
            errors.append(ErrorUseTupleWithInExpr(expr.line, expr.column))
