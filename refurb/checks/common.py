from collections.abc import Callable
from itertools import chain, combinations, starmap

from mypy.nodes import (
    Block,
    CallExpr,
    ComparisonExpr,
    DictExpr,
    DictionaryComprehension,
    Expression,
    ForStmt,
    GeneratorExpr,
    IndexExpr,
    ListExpr,
    MemberExpr,
    MypyFile,
    NameExpr,
    Node,
    OpExpr,
    SetExpr,
    SliceExpr,
    StarExpr,
    Statement,
    TupleExpr,
    UnaryExpr,
)
from mypy.traverser import TraverserVisitor

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


def check_for_loop_like(
    func: Callable[[Node, Node, list[Node], list[Error]], None],
    node: ForStmt | GeneratorExpr | DictionaryComprehension,
    errors: list[Error],
) -> None:
    match node:
        case ForStmt(index=index, expr=expr):
            func(index, expr, [], errors)

        case GeneratorExpr(
            indices=[index],
            sequences=[expr],
            condlists=condlists,
        ):
            func(
                index,
                expr,
                list(chain([node.left_expr], *condlists)),
                errors,
            )

        case DictionaryComprehension(
            indices=[index],
            sequences=[expr],
            condlists=condlists,
        ):
            func(
                index,
                expr,
                list(chain([node.key, node.value], *condlists)),
                errors,
            )


def unmangle_name(name: str | None) -> str:
    return (name or "").replace("'", "")


def is_equivalent(lhs: Node | None, rhs: Node | None) -> bool:
    match (lhs, rhs):
        case None, None:
            return True

        case NameExpr() as lhs, NameExpr() as rhs:
            return unmangle_name(lhs.fullname) == unmangle_name(rhs.fullname)

        case MemberExpr() as lhs, MemberExpr() as rhs:
            return (
                lhs.name == rhs.name
                and unmangle_name(lhs.fullname) == unmangle_name(rhs.fullname)
                and is_equivalent(lhs.expr, rhs.expr)
            )

        case IndexExpr() as lhs, IndexExpr() as rhs:
            return is_equivalent(lhs.base, rhs.base) and is_equivalent(
                lhs.index, rhs.index
            )

        case CallExpr() as lhs, CallExpr() as rhs:
            return (
                is_equivalent(lhs.callee, rhs.callee)
                and all(starmap(is_equivalent, zip(lhs.args, rhs.args)))
                and lhs.arg_kinds == rhs.arg_kinds
                and lhs.arg_names == rhs.arg_names
            )

        case (
            (ListExpr() as lhs, ListExpr() as rhs)
            | (TupleExpr() as lhs, TupleExpr() as rhs)
            | (SetExpr() as lhs, SetExpr() as rhs)
        ):
            return len(lhs.items) == len(rhs.items) and all(  # type: ignore
                starmap(
                    is_equivalent, zip(lhs.items, rhs.items)  # type: ignore
                )
            )

        case DictExpr() as lhs, DictExpr() as rhs:
            return len(lhs.items) == len(rhs.items) and all(
                is_equivalent(lhs_item[0], rhs_item[0])
                and is_equivalent(lhs_item[1], rhs_item[1])
                for lhs_item, rhs_item in zip(lhs.items, rhs.items)
            )

        case StarExpr() as lhs, StarExpr() as rhs:
            return is_equivalent(lhs.expr, rhs.expr)

        case UnaryExpr() as lhs, UnaryExpr() as rhs:
            return lhs.op == rhs.op and is_equivalent(lhs.expr, rhs.expr)

        case OpExpr() as lhs, OpExpr() as rhs:
            return (
                lhs.op == rhs.op
                and is_equivalent(lhs.left, rhs.left)
                and is_equivalent(lhs.right, rhs.right)
            )

        case ComparisonExpr() as lhs, ComparisonExpr() as rhs:
            return lhs.operators == rhs.operators and all(
                starmap(is_equivalent, zip(lhs.operands, rhs.operands))
            )

        case SliceExpr() as lhs, SliceExpr() as rhs:
            return (
                is_equivalent(lhs.begin_index, rhs.begin_index)
                and is_equivalent(lhs.end_index, rhs.end_index)
                and is_equivalent(lhs.stride, rhs.stride)
            )

    return str(lhs) == str(rhs)


def get_common_expr_positions(*exprs: Expression) -> tuple[int, int] | None:
    for lhs, rhs in combinations(exprs, 2):
        if is_equivalent(lhs, rhs):
            return exprs.index(lhs), exprs.index(rhs)

    return None


def get_common_expr_in_comparison_chain(
    node: OpExpr, oper: str, cmp_oper: str = "=="
) -> tuple[Expression, tuple[int, int]] | None:
    """
    This function finds the first expression shared between 2 comparison
    expressions in the binary operator `oper`.

    For example, an OpExpr that looks like the following:

    1 == 2 or 3 == 1

    Will return a tuple containing the first common expression (`IntExpr(1)` in
    this case), and the indices of the common expressions as they appear in the
    source (`0` and `3` in this case). The indices are to be used for display
    purposes by the caller.

    If the binary operator is not composed of 2 comparison operators, or if
    there are no common expressions, `None` is returned.
    """

    match extract_binary_oper(oper, node):
        case (
            ComparisonExpr(operators=[lhs_oper], operands=[a, b]),
            ComparisonExpr(operators=[rhs_oper], operands=[c, d]),
        ) if (
            lhs_oper == rhs_oper == cmp_oper
            and (indices := get_common_expr_positions(a, b, c, d))
        ):
            return a, indices

    return None  # pragma: no cover


class ReadCountVisitor(TraverserVisitor):
    name: NameExpr
    read_count: int

    def __init__(self, name: NameExpr) -> None:
        self.name = name
        self.read_count = 0

    def visit_name_expr(self, node: NameExpr) -> None:
        if node.fullname == self.name.fullname:
            self.read_count += 1

    @property
    def was_read(self) -> int:
        return self.read_count > 0


def is_placeholder(name: NameExpr) -> bool:
    return unmangle_name(name.name) == "_"


def is_name_unused_in_contexts(name: NameExpr, contexts: list[Node]) -> bool:
    if not contexts:
        return False

    for ctx in contexts:
        visitor = ReadCountVisitor(name)
        ctx.accept(visitor)

        if visitor.was_read:
            return False

    return True


def normalize_os_path(module: str) -> str:
    """
    Mypy turns "os.path" module names into their respective platform, such
    as "ntpath" for windows, "posixpath" if they are POSIX only, or
    "genericpath" if they apply to both (I assume). To make life easier
    for us though, we turn those module names into their original form.
    """

    segments = module.split(".")

    if segments[0].startswith(("genericpath", "ntpath", "posixpath")):
        return ".".join(["os", "path"] + segments[1:])

    return module
