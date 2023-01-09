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
    NameExpr,
    Node,
    OpExpr,
    StrExpr,
    TupleExpr,
    UnaryExpr,
    Var,
    WhileStmt,
)
from mypy.traverser import TraverserVisitor

from refurb.error import Error
from refurb.visitor import METHOD_NODE_MAPPINGS


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
    categories = ["iterable", "truthy"]


CONTAINER_TYPES = {
    "builtins.list",
    "builtins.tuple",
    "builtins.dict",
    "builtins.set",
    "builtins.frozenset",
    "builtins.str",
    "Tuple",
}


def is_builtin_container_type(type: str) -> bool:
    return any(type.startswith(x) for x in CONTAINER_TYPES)


def is_builtin_container_like(node: Expression) -> bool:
    match node:
        case NameExpr(node=Var(type=ty)) if is_builtin_container_type(str(ty)):
            return True

        case CallExpr(
            callee=NameExpr(fullname=name)
        ) if is_builtin_container_type(name or ""):
            return True

        case DictExpr() | ListExpr() | StrExpr() | TupleExpr():
            return True

    return False


def is_len_call(node: CallExpr) -> bool:
    match node:
        case CallExpr(
            callee=NameExpr(fullname="builtins.len"),
            args=[arg],
        ) if is_builtin_container_like(arg):
            return True

    return False


IS_INT_COMPARISON_TRUTHY: dict[tuple[str, int], bool] = {
    ("==", 0): False,
    ("<=", 0): False,
    (">", 0): True,
    ("!=", 0): True,
    (">=", 1): True,
}


class LenComparisonVisitor(TraverserVisitor):
    errors: list[Error]

    def __init__(self, errors: list[Error]) -> None:
        super().__init__()

        self.errors = errors

        for name, ty in METHOD_NODE_MAPPINGS.items():
            if ty in (ComparisonExpr, UnaryExpr, OpExpr, CallExpr):
                continue

            def inner(self: "LenComparisonVisitor", o: Node) -> None:
                return

            setattr(self, name, inner.__get__(self))

    def visit_comparison_expr(self, node: ComparisonExpr) -> None:
        match node:
            case ComparisonExpr(
                operators=[oper],
                operands=[CallExpr() as call, IntExpr(value=num)],
            ) if is_len_call(call):
                is_truthy = IS_INT_COMPARISON_TRUTHY.get((oper, num))

                if is_truthy is None:
                    return

                expr = "x" if is_truthy else "not x"

                self.errors.append(
                    ErrorInfo(
                        node.line,
                        node.column,
                        f"Replace `len(x) {oper} {num}` with `{expr}`",
                    )
                )

            case ComparisonExpr(
                operators=["==" | "!=" as oper],
                operands=[
                    NameExpr() as name,
                    (ListExpr() | DictExpr()) as expr,
                ],
            ) if is_builtin_container_like(name):
                if expr.items:  # type: ignore
                    return

                old_expr = "[]" if isinstance(expr, ListExpr) else "{}"
                expr = "not x" if oper == "==" else "x"

                self.errors.append(
                    ErrorInfo(
                        node.line,
                        node.column,
                        f"Replace `x {oper} {old_expr}` with `{expr}`",
                    )
                )

    def visit_call_expr(self, node: CallExpr) -> None:
        if is_len_call(node):
            self.errors.append(
                ErrorInfo(node.line, node.column, "Replace `len(x)` with `x`")
            )


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
                expr.accept(visitor)

        case MatchStmt(guards=guards) if guards:
            for guard in guards:
                if guard:
                    guard.accept(visitor)

        case (
            GeneratorExpr(condlists=conditions)
            | DictionaryComprehension(condlists=conditions)
        ):
            for condition in conditions:
                for expr in condition:
                    expr.accept(visitor)

        case (
            ConditionalExpr(cond=expr)
            | WhileStmt(expr=expr)
            | AssertStmt(expr=expr)
        ):
            expr.accept(visitor)
