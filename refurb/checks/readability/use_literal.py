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


FUNC_NAMES = {
    "builtins.bool": "False",
    "builtins.bytes": 'b""',
    "builtins.complex": "0j",
    "builtins.dict": "{}",
    "builtins.float": "0.0",
    "builtins.int": "0",
    "builtins.list": "[]",
    "builtins.str": '""',
    "builtins.tuple": "()",
}


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=NameExpr(fullname=fullname, name=name),
            args=[],
        ) if fullname in FUNC_NAMES.keys():
            newer = FUNC_NAMES[fullname or ""]

            errors.append(
                ErrorUseLiteral(
                    node.line,
                    node.column,
                    f"Use `{newer}` instead of `{name}()`",
                )
            )
