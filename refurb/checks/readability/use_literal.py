from dataclasses import dataclass

from mypy.nodes import CallExpr, NameExpr

from refurb.error import Error


@dataclass
class ErrorUseLiteral(Error):
    """
    Using `list` and `dict` without any arguments is slower, and not Pythonic.
    Use `[]` and `{}` instead:

    Bad:

    ```
    nums = list()
    books = dict()
    ```

    Good:

    ```
    nums = []
    books = {}
    ```
    """

    code = 112


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=NameExpr(fullname=name),
            args=[],
        ) if name in ("builtins.list", "builtins.dict"):
            older = "list()" if "list" in name else "dict()"
            newer = "[]" if "list" in name else "{}"

            errors.append(
                ErrorUseLiteral(
                    node.line,
                    node.column,
                    f"Use `{newer}` instead of `{older}`",
                )
            )
