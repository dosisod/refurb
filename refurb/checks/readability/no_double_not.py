from dataclasses import dataclass

from mypy.nodes import UnaryExpr

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Double negatives are confusing, so use `bool(x)` instead of `not not x`.

    Bad:

    ```
    if not not value:
        pass
    ```

    Good:

    ```
    if bool(value):
        pass
    ```
    """

    code = 114
    msg: str = "Use `bool(x)` instead of `not not x`"


def check(node: UnaryExpr, errors: list[Error]) -> None:
    match node:
        case UnaryExpr(op="not", expr=UnaryExpr(op="not")):
            errors.append(ErrorInfo(node.line, node.column))
