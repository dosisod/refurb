from dataclasses import dataclass

from mypy.nodes import (
    Block,
    Expression,
    FuncItem,
    IfStmt,
    MatchStmt,
    ReturnStmt,
    Statement,
)
from mypy.patterns import AsPattern

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Sometimes a return statement can be written more succinctly:

    Bad:

    ```
    def index_or_default(nums: list[Any], index: int, default: Any):
        if index >= len(nums):
            return default

        else:
            return nums[index]

    def is_on_axis(position: tuple[int, int]) -> bool:
        match position:
            case (0, _) | (_, 0):
                return True

            case _:
                return False
    ```

    Good:

    ```
    def index_or_default(nums: list[Any], index: int, default: Any):
        if index >= len(nums):
            return default

        return nums[index]

    def is_on_axis(position: tuple[int, int]) -> bool:
        match position:
            case (0, _) | (_, 0):
                return True

        return False
    ```
    """

    name = "simplify-return"
    code = 126
    categories = ["control-flow", "readability"]


def get_trailing_return(node: Statement) -> Statement | None:
    match node:
        case ReturnStmt(expr=Expression()):
            return node

        case MatchStmt(
            bodies=[*bodies, Block(body=[stmt])],
            patterns=[*_, AsPattern(pattern=None)],
        ) if all(isinstance(block.body[-1], ReturnStmt) for block in bodies):
            return get_trailing_return(stmt)

        case IfStmt(
            body=[Block(body=[*_, ReturnStmt()])], else_body=Block(body=[stmt])
        ):
            return get_trailing_return(stmt)

    return None


def check(node: FuncItem, errors: list[Error]) -> None:
    match node:
        case FuncItem(body=Block(body=[*_, IfStmt() | MatchStmt() as stmt])):
            if return_node := get_trailing_return(stmt):
                name = "case _" if type(stmt) is MatchStmt else "else"

                errors.append(
                    ErrorInfo(
                        return_node.line,
                        return_node.column,
                        f"Replace `{name}: return x` with `return x`",
                    )
                )
