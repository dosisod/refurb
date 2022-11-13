from collections.abc import Callable

from mypy.nodes import (
    Block,
    Expression,
    MemberExpr,
    MypyFile,
    NameExpr,
    Node,
    OpExpr,
    Statement,
)

from refurb.error import Error


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

                case OpExpr():
                    return None

                case Expression():
                    return lhs, rhs

    return None


def check_block_like(
    func: Callable[[list[Statement], list[Error]], None],
    node: Block | MypyFile,
    errors: list[Error],
) -> None:
    match node:
        case Block():
            func(node.body, errors)

        case MypyFile():
            func(node.defs, errors)


def unmangle_name(name: str | None) -> str:
    return (name or "").replace("'", "")


def is_equivalent(lhs: Node, rhs: Node) -> bool:
    match (lhs, rhs):
        case NameExpr() as lhs, NameExpr() as rhs:
            return unmangle_name(lhs.fullname) == unmangle_name(rhs.fullname)

        case MemberExpr() as lhs, MemberExpr() as rhs:
            return (
                lhs.name == rhs.name
                and unmangle_name(lhs.fullname) == unmangle_name(rhs.fullname)
                and is_equivalent(lhs.expr, rhs.expr)
            )

    return str(lhs) == str(rhs)
