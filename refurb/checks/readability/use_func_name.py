from dataclasses import dataclass

from mypy.nodes import (
    ArgKind,
    Argument,
    Block,
    CallExpr,
    Expression,
    LambdaExpr,
    NameExpr,
    ReturnStmt,
)

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
    msg: str = "Replace `lambda x: f(x)` with `f`"
    categories = ["readability"]


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
                    ReturnStmt(
                        expr=CallExpr(callee=NameExpr(name=func_name)) as func
                    ),
                ]
            ),
        ) if (
            get_lambda_arg_names(lambda_args) == get_func_arg_names(func.args)
            and all(kind == ArgKind.ARG_POS for kind in func.arg_kinds)
        ):
            arg_names = get_lambda_arg_names(lambda_args)
            arg_names = ", ".join(arg_names) if arg_names else ""

            _lambda = f"lambda {arg_names}" if arg_names else "lambda"

            errors.append(
                ErrorInfo(
                    node.line,
                    node.column,
                    f"Replace `{_lambda}: {func_name}({arg_names})` with `{func_name}`",  # noqa: E501
                )
            )
