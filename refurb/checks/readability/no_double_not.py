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

    name = "no-double-not"
    code = 114
    msg: str = "Replace `not not x` with `bool(x)`"
    categories = ["builtin", "readability", "truthy"]


def check(node: UnaryExpr, errors: list[Error]) -> None:
    match node:
        case UnaryExpr(op="not", expr=UnaryExpr(op="not")):
            errors.append(ErrorInfo(node.line, node.column))
