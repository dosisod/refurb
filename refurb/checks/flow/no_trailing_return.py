from dataclasses import dataclass
from typing import Generator

from mypy.nodes import (
    Block,
    FuncItem,
    IfStmt,
    MatchStmt,
    ReturnStmt,
    Statement,
    WithStmt,
)
from mypy.patterns import AsPattern

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
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
            print("x is not 1")

            return
    ```

    Good:

    ```
    def func():
        print("hello world!")

    def func2(x):
        if x == 1:
            print("x is 1")

        else:
            print("x is not 1")
    ```
    """

    name = "no-redundant-return"
    code = 125
    msg: str = "Return is redundant here"
    categories = ["control-flow", "readability"]


def get_trailing_return(node: Statement) -> Generator[Statement, None, None]:
    match node:
        case ReturnStmt(expr=None):
            yield node

        case MatchStmt(bodies=bodies, patterns=patterns):
            for body, pattern in zip(bodies, patterns):
                match (body.body, pattern):
                    case _, AsPattern(pattern=None, name=None):
                        pass

                    case [ReturnStmt()], _:
                        continue

                yield from get_trailing_return(body.body[-1])

        case (
            IfStmt(else_body=Block(body=[*_, stmt]))
            | WithStmt(body=Block(body=[*_, stmt]))
        ):
            yield from get_trailing_return(stmt)

    return None


def check(node: FuncItem, errors: list[Error]) -> None:
    match node:
        case FuncItem(body=Block(body=[*prev, stmt])):
            if not prev and isinstance(stmt, ReturnStmt):
                return

            for return_node in get_trailing_return(stmt):
                errors.append(ErrorInfo(return_node.line, return_node.column))
