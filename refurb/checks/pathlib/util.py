from mypy.nodes import CallExpr, Expression, NameExpr, TypeInfo, Var


def is_pathlike(expr: Expression) -> bool:
    match expr:
        case CallExpr(
            callee=NameExpr(node=TypeInfo() as ty),
        ) if ty.fullname == "pathlib.Path":
            return True

        case NameExpr(node=Var(type=ty)) if str(ty) == "pathlib.Path":
            return True

    return False
