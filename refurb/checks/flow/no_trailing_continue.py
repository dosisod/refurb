from dataclasses import dataclass
from typing import Generator

from mypy.nodes import (
    Block,
    ContinueStmt,
    ForStmt,
    IfStmt,
    MatchStmt,
    Statement,
    WhileStmt,
    WithStmt,
)
from mypy.patterns import AsPattern

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Don't explicitly continue if you are already at the end of the control flow
    for the current for/while loop:

    Bad:

    ```
    def func():
        for _ in range(10):
            print("hello world!")

            continue

    def func2(x):
        for x in range(10):
            if x == 1:
                print("x is 1")

            else:
                print("x is not 1")

                continue
    ```

    Good:

    ```
    def func():
        for _ in range(10):
            print("hello world!")

    def func2(x):
        for x in range(10):
            if x == 1:
                print("x is 1")

            else:
                print("x is not 1")
    ```
    """

    name = "no-redundant-continue"
    code = 133
    msg: str = "Continue is redundant here"
    categories = ["control-flow", "readability"]


def get_trailing_continue(node: Statement) -> Generator[Statement, None, None]:
    match node:
        case ContinueStmt():
            yield node

        case MatchStmt(bodies=bodies, patterns=patterns):
            for body, pattern in zip(bodies, patterns):
                match (body.body, pattern):
                    case _, AsPattern(pattern=None, name=None):
                        pass

                    case [ContinueStmt()], _:
                        continue

                yield from get_trailing_continue(body.body[-1])

        case (
            IfStmt(else_body=Block(body=[*_, stmt]))
            | WithStmt(body=Block(body=[*_, stmt]))
        ):
            yield from get_trailing_continue(stmt)

    return None


def check(node: ForStmt | WhileStmt, errors: list[Error]) -> None:
    match node:
        case (
            ForStmt(body=Block(body=[*prev, stmt]))
            | WhileStmt(body=Block(body=[*prev, stmt]))
        ):
            if not prev and isinstance(stmt, ContinueStmt):
                return

            for continue_node in get_trailing_continue(stmt):
                errors.append(
                    ErrorInfo(continue_node.line, continue_node.column)
                )
