from mypy.nodes import Expression, OpExpr


def extract_binary_oper(
    oper: str, node: OpExpr
) -> tuple[Expression, Expression] | None:
    match node:
        case OpExpr(
            op=op,
            left=lhs,
            right=rhs,
        ) if op == oper:
            match rhs:
                case OpExpr(op=op, left=rhs) if op == oper:
                    return lhs, rhs

                case Expression():
                    return lhs, rhs

    return None
