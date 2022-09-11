from dataclasses import dataclass

from mypy.nodes import (
    Block,
    FuncItem,
    IfStmt,
    MatchStmt,
    ReturnStmt,
    Statement,
    WithStmt,
)

from refurb.error import Error


@dataclass
class ErrorNoTrailingReturn(Error):
    """
    Don't explicitly return if you are already at the end of the control flow
    for the current function:

    Bad:

    ```
    def func():
        print("hello world!")

        return

    def func2(x):
        if x == 1:
            print("x is 1")

        else:
            return
    ```

    Good:

    ```
    def func():
        print("hello world!")

    def func2(x):
        if x == 1:
            print("x is 1")
    ```
    """

    code = 125
    msg: str = "Return is redundant here"


def get_trailing_return(node: Statement) -> Statement | None:
    match node:
        case ReturnStmt(expr=None) as stmt:
            return stmt

        case (
            MatchStmt(bodies=[*_, Block(body=[*_, stmt])])
            | IfStmt(else_body=Block(body=[*_, stmt]))
            | WithStmt(body=Block(body=[*_, stmt]))
        ) if return_node := get_trailing_return(stmt):
            return return_node

    return None


def check(node: FuncItem, errors: list[Error]) -> None:
    match node:
        case FuncItem(body=Block(body=[*_, stmt])):
            if return_node := get_trailing_return(stmt):
                errors.append(
                    ErrorNoTrailingReturn(return_node.line, return_node.column)
                )
