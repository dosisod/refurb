from dataclasses import dataclass

from mypy.nodes import (
    ArgKind,
    Argument,
    Block,
    CallExpr,
    DictExpr,
    Expression,
    LambdaExpr,
    ListExpr,
    NameExpr,
    RefExpr,
    ReturnStmt,
    TupleExpr,
)

from refurb.checks.common import stringify
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Don't use a lambda if it is just forwarding its arguments to a
    function verbatim:

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
    """

    name = "use-func-name"
    code = 111
    categories = ("readability",)


def get_lambda_arg_names(args: list[Argument]) -> list[str]:
    return [arg.variable.name for arg in args]


def get_func_arg_names(args: list[Expression]) -> list[str | None]:
    return [arg.name if isinstance(arg, NameExpr) else None for arg in args]


def check(node: LambdaExpr, errors: list[Error]) -> None:
    match node:
        case LambdaExpr(
            arguments=lambda_args,
            body=Block(
                body=[
                    ReturnStmt(expr=CallExpr(callee=RefExpr() as ref) as func),
                ]
            ),
        ) if (
            get_lambda_arg_names(lambda_args) == get_func_arg_names(func.args)
            and all(kind == ArgKind.ARG_POS for kind in func.arg_kinds)
        ):
            func_name = stringify(ref)
            arg_names = get_lambda_arg_names(lambda_args)
            arg_names = ", ".join(arg_names) if arg_names else ""

            _lambda = f"lambda {arg_names}" if arg_names else "lambda"

            errors.append(
                ErrorInfo.from_node(
                    node,
                    f"Replace `{_lambda}: {func_name}({arg_names})` with `{func_name}`",  # noqa: E501
                )
            )

        case LambdaExpr(
            arguments=[],
            body=Block(
                body=[
                    ReturnStmt(
                        expr=ListExpr(items=[]) | DictExpr(items=[]) | TupleExpr(items=[]) as expr,
                    )
                ],
            ),
        ):
            if isinstance(expr, ListExpr):
                old = "[]"
                new = "list"
            elif isinstance(expr, DictExpr):
                old = "{}"
                new = "dict"
            else:
                old = "()"
                new = "tuple"

            errors.append(
                ErrorInfo.from_node(
                    node,
                    f"Replace `lambda: {old}` with `{new}`",
                )
            )
