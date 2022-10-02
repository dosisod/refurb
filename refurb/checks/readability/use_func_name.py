from dataclasses import dataclass

from mypy.nodes import (
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

    code = 111
    msg: str = "Use `f` instead of `lambda x: f(x)`"


def get_lambda_arg_names(args: list[Argument]) -> list[str]:
    return [arg.variable.name for arg in args]


def get_func_names(args: list[Expression]) -> list[str] | None:
    names = []

    for arg in args:
        if not isinstance(arg, NameExpr):
            return None

        names.append(arg.name)

    return names


def check(node: LambdaExpr, errors: list[Error]) -> None:
    match node:
        case LambdaExpr(
            arguments=lambda_args,
            body=Block(body=[ReturnStmt(expr=CallExpr(args=func_args))]),
        ) if get_lambda_arg_names(lambda_args) == get_func_names(func_args):
            errors.append(ErrorInfo(node.line, node.column))
