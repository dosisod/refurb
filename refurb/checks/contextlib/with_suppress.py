from dataclasses import dataclass
from typing import cast

from mypy.nodes import Block, NameExpr, PassStmt, TryStmt, TupleExpr

from refurb.error import Error


@dataclass
class ErrorUseWithSuppress(Error):
    """
    Often times you want to handle an exception, and just ignore it. You can do
    this with a `try/except` block, using a single `pass` in the `except`
    block, but there is a simpler and more consice way using the `suppress()`
    method from `contextlib`:

    Bad:

    ```
    try:
        f()

    except FileNotFoundError:
        pass
    ```

    Good:

    ```
    with suppress(FileNotFoundError):
        f()
    ```
    """

    code = 107


def check(node: TryStmt, errors: list[Error]) -> None:
    match node:
        case TryStmt(
            handlers=[Block(body=[PassStmt()])],
            types=[types],
            else_body=None,
            finally_body=None,
        ):
            inner = ""

            match types:
                case NameExpr(name=name):
                    inner = name

                case TupleExpr(items=items):
                    tmp = ", ".join(cast(NameExpr, exc).name for exc in items)
                    inner = f"({tmp})"

            errors.append(
                ErrorUseWithSuppress(
                    node.line,
                    node.column,
                    f"Use `with suppress({inner}): ...` instead of `try: ... except: pass`",  # noqa: E501
                )
            )
