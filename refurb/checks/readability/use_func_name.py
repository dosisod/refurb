from dataclasses import dataclass

from mypy.nodes import (
    ArgKind,
    Argument,
    Block,
    BytesExpr,
    CallExpr,
    ComplexExpr,
    DictExpr,
    Expression,
    FloatExpr,
    IntExpr,
    LambdaExpr,
    ListExpr,
    NameExpr,
    RefExpr,
    ReturnStmt,
    StrExpr,
    TupleExpr,
)

from refurb.checks.common import stringify
from refurb.error import Error
from refurb.visitor.traverser import TraverserVisitor


@dataclass
class ErrorInfo(Error):
    """
    Don't use a lambda if its only forwarding its arguments to a function.

    Bad:

    ```
    predicate = lambda x: bool(x)

    some_func(lambda x, y: print(x, y))
    ```

    Good:

    ```
    predicate = bool

    some_func(print)
    ```

    In addition, don't use lambdas when you want a default value for a literal
    type:

    Bad:

    ```
    counter = defaultdict(lambda: 0)
    multimap = defaultdict(lambda: [])
    ```

    Good:

    ```
    counter = defaultdict(int)
    multimap = defaultdict(list)
    ```
    """

    name = "use-func-name"
    code = 111
    categories = ("performance", "readability")


def get_lambda_arg_names(args: list[Argument]) -> list[str]:
    return [arg.variable.name for arg in args]


def get_func_arg_names(args: list[Expression]) -> list[str | None]:
    return [arg.name if isinstance(arg, NameExpr) else None for arg in args]


class ContainsCallExpr(TraverserVisitor):
    def __init__(self) -> None:
        self.has_call_expr = False

    def visit_call_expr(self, o: CallExpr) -> None:  # noqa: ARG002
        self.has_call_expr = True


def does_expr_contain_call_expr(expr: Expression) -> bool:
    visitor = ContainsCallExpr()
    visitor.accept(expr)

    return visitor.has_call_expr


def check(node: LambdaExpr, errors: list[Error]) -> None:
    match node:
        case LambdaExpr(
            arguments=lambda_args,
            body=Block(
                body=[ReturnStmt(expr=CallExpr(callee=RefExpr() as ref) as func)],
            ),
        ) if (
            get_lambda_arg_names(lambda_args) == get_func_arg_names(func.args)
            and all(kind == ArgKind.ARG_POS for kind in func.arg_kinds)
            and not does_expr_contain_call_expr(ref)
        ):
            func_name = stringify(ref)

            msg = f"Replace `{stringify(node)}` with `{func_name}`"

            errors.append(ErrorInfo.from_node(node, msg))

        case LambdaExpr(
            arguments=[],
            body=Block(
                body=[
                    ReturnStmt(
                        expr=(
                            ListExpr(items=[])
                            | DictExpr(items=[])
                            | TupleExpr(items=[])
                            | IntExpr(value=0)
                            | FloatExpr(value=0.0)
                            | ComplexExpr(value=0j)
                            | NameExpr(fullname="builtins.False")
                            | StrExpr(value="")
                            | BytesExpr(value="")
                        ) as expr,
                    )
                ],
            ),
        ):
            if isinstance(expr, ListExpr):
                new = "list"
            elif isinstance(expr, DictExpr):
                new = "dict"
            elif isinstance(expr, TupleExpr):
                new = "tuple"
            elif isinstance(expr, IntExpr):
                new = "int"
            elif isinstance(expr, FloatExpr):
                new = "float"
            elif isinstance(expr, ComplexExpr):
                new = "complex"
            elif isinstance(expr, NameExpr):
                new = "bool"
            elif isinstance(expr, StrExpr):
                new = "str"
            elif isinstance(expr, BytesExpr):
                new = "bytes"
            else:
                assert False, "unreachable"  # noqa: B011

            msg = f"Replace `{stringify(node)}` with `{new}`"

            errors.append(ErrorInfo.from_node(node, msg))
