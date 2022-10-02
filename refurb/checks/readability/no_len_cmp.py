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
    StrExpr,
    TupleExpr,
    Var,
    WhileStmt,
)
from mypy.traverser import TraverserVisitor

from refurb.error import Error


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

    code = 115


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


IS_COMPARISON_TRUTHY: dict[tuple[str, int], bool] = {
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

    def visit_comparison_expr(self, o: ComparisonExpr) -> None:
        super().visit_comparison_expr(o)

        check_comparison(o, self.errors)


def check_comparison(node: ComparisonExpr, errors: list[Error]) -> None:
    match node:
        case ComparisonExpr(
            operators=[oper],
            operands=[
                CallExpr(
                    callee=NameExpr(fullname="builtins.len"),
                    args=[arg],
                ),
                IntExpr(value=num),
            ],
        ) if is_builtin_container_like(arg):
            is_truthy = IS_COMPARISON_TRUTHY.get((oper, num))

            if is_truthy is None:
                return

            expr = "x" if is_truthy else "not x"

            errors.append(
                ErrorInfo(
                    node.line,
                    node.column,
                    f"Use `{expr}` instead of `len(x) {oper} {num}`",
                )
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
