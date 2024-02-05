from mypy.nodes import CallExpr, Expression, NameExpr, OpExpr, RefExpr, Var

from refurb.checks.common import is_same_type


def is_pathlike(expr: Expression) -> bool:
    # TODO: just check that the expression is of type `Path` once we actually
    # get proper type checking
    match expr:
        case CallExpr(callee=RefExpr(fullname="pathlib.Path")):
            return True

        case NameExpr(node=Var(type=ty)) if is_same_type(ty, "pathlib.Path"):
            return True

        case OpExpr(left=left, op="/") if is_pathlike(left):
            return True

    return False
