from dataclasses import dataclass

from mypy.nodes import (
    AssertStmt,
    CallExpr,
    ComparisonExpr,
    ConditionalExpr,
    DictExpr,
    DictionaryComprehension,
    Expression,
    GeneratorExpr,
    IfStmt,
    IntExpr,
    ListExpr,
    MatchStmt,
    MemberExpr,
    NameExpr,
    Node,
    OpExpr,
    TupleExpr,
    UnaryExpr,
    WhileStmt,
)

from refurb.checks.common import (
    get_mypy_type,
    is_mapping,
    is_same_type,
    is_sized,
    mypy_type_to_python_type,
    stringify,
)
from refurb.error import Error
from refurb.visitor import METHOD_NODE_MAPPINGS, TraverserVisitor


@dataclass
class ErrorInfo(Error):
    """
    Don't check a container's length to determine if it is empty or not, use
    a truthiness check instead:

    Bad:

    ```
    name = "bob"
    if len(name) == 0:
        pass

    nums = [1, 2, 3]
    if len(nums) >= 1:
        pass
    ```

    Good:

    ```
    name = "bob"
    if not name:
        pass

    nums = [1, 2, 3]
    if nums:
        pass
    ```
    """

    name = "no-len-compare"
    code = 115
    categories = ("iterable", "truthy")


def is_len_call(node: CallExpr) -> bool:
    match node:
        case CallExpr(callee=NameExpr(fullname="builtins.len"), args=[arg]) if is_sized(arg):
            return True

    return False


IS_INT_COMPARISON_TRUTHY: dict[tuple[str, int], bool] = {
    ("==", 0): False,
    ("<=", 0): False,
    (">", 0): True,
    ("!=", 0): True,
    (">=", 1): True,
}


def simplify_len_call(expr: Expression) -> Expression:
    match expr:
        case CallExpr(callee=NameExpr(fullname="builtins.list"), args=[arg]):
            return simplify_len_call(arg)

        case CallExpr(
            callee=MemberExpr(expr=arg, name="keys" | "values"),
            args=[],
        ) if is_mapping(arg):
            return simplify_len_call(arg)

    return expr


class LenComparisonVisitor(TraverserVisitor):
    errors: list[Error]

    def __init__(self, errors: list[Error]) -> None:
        super().__init__()

        self.errors = errors

        for name, ty in METHOD_NODE_MAPPINGS.items():
            if ty in {ComparisonExpr, UnaryExpr, OpExpr, CallExpr}:
                continue

            def inner(self: "LenComparisonVisitor", _: Node) -> None:
                return

            setattr(self, name, inner.__get__(self))

    def visit_op_expr(self, o: OpExpr) -> None:
        if o.op in {"and", "or"}:
            super().visit_op_expr(o)

    def visit_comparison_expr(self, node: ComparisonExpr) -> None:
        match node:
            case ComparisonExpr(
                operators=[oper],
                operands=[CallExpr(args=[arg]) as call, IntExpr(value=num)],
            ) if is_len_call(call):
                is_truthy = IS_INT_COMPARISON_TRUTHY.get((oper, num))

                if is_truthy is None:
                    return

                arg = simplify_len_call(arg)

                old = stringify(node)
                new = stringify(arg)

                if not is_truthy:
                    new = f"not {new}"

                msg = f"Replace `{old}` with `{new}`"

                self.errors.append(ErrorInfo.from_node(node, msg))

            case ComparisonExpr(
                operators=["==" | "!=" as oper],
                operands=[
                    lhs,
                    (
                        ListExpr(items=[])
                        | DictExpr(items=[])
                        | TupleExpr(items=[])
                        | CallExpr(
                            callee=NameExpr(fullname="builtins.set" | "builtins.frozenset"),
                            args=[],
                        )
                    ) as rhs,
                ],
            ) if is_same_type(get_mypy_type(lhs), mypy_type_to_python_type(get_mypy_type(rhs))):
                old = stringify(node)
                new = stringify(lhs)

                if oper == "==":
                    new = f"not {new}"

                msg = f"Replace `{old}` with `{new}`"

                self.errors.append(ErrorInfo.from_node(node, msg))

    def visit_call_expr(self, node: CallExpr) -> None:
        if is_len_call(node):
            msg = f"Replace `{stringify(node)}` with `{stringify(node.args[0])}`"

            self.errors.append(ErrorInfo.from_node(node, msg))


ConditionLikeNode = (
    IfStmt
    | MatchStmt
    | GeneratorExpr
    | DictionaryComprehension
    | ConditionalExpr
    | WhileStmt
    | AssertStmt
)


def check(node: ConditionLikeNode, errors: list[Error]) -> None:
    check_condition_like(LenComparisonVisitor(errors), node)


def check_condition_like(
    visitor: TraverserVisitor,
    node: ConditionLikeNode,
) -> None:
    match node:
        case IfStmt(expr=exprs):
            for expr in exprs:
                visitor.accept(expr)

        case MatchStmt(guards=guards) if guards:
            for guard in guards:
                if guard:
                    visitor.accept(guard)

        case GeneratorExpr(condlists=conditions) | DictionaryComprehension(condlists=conditions):
            for condition in conditions:
                for expr in condition:
                    visitor.accept(expr)

        case ConditionalExpr(cond=expr) | WhileStmt(expr=expr) | AssertStmt(expr=expr):
            visitor.accept(expr)
