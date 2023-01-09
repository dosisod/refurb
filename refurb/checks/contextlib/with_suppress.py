from dataclasses import dataclass

from mypy.nodes import Block, NameExpr, PassStmt, TryStmt, TupleExpr

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Often times you want to handle an exception, and just ignore it. You can do
    this with a `try/except` block, using a single `pass` in the `except`
    block, but there is a simpler and more concise way using the `suppress()`
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

    name = "use-with-suppress"
    code = 107
    categories = ["contextlib", "readability"]


def check(node: TryStmt, errors: list[Error]) -> None:
    match node:
        case TryStmt(
            handlers=[Block(body=[PassStmt()])],
            types=[types],
            else_body=None,
            finally_body=None,
        ):
            match types:
                case NameExpr(name=name):
                    inner = name
                    except_inner = f" {inner}"

                case TupleExpr(items=items):
                    if any(not isinstance(item, NameExpr) for item in items):
                        return

                    inner = ", ".join(
                        item.name for item in items  # type: ignore
                    )

                    except_inner = f" ({inner})"

                case None:
                    inner = "BaseException"
                    except_inner = ""

                case _:
                    return

            errors.append(
                ErrorInfo(
                    node.line,
                    node.column,
                    f"Replace `try: ... except{except_inner}: pass` with `with suppress({inner}): ...`",  # noqa: E501
                )
            )
