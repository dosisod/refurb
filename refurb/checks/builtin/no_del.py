from dataclasses import dataclass

from mypy.nodes import DelStmt, IndexExpr, NameExpr, SliceExpr, Var

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    The `del` statement has it's uses, but for the most part, it can be
    replaced with a more flexible and expressive alternative.

    With `dict` and `list` types you can remove a key/index by using the
    `.pop()` method. If you want to remove all the elements in a `dict` or
    `list`, use `.clear()` instead.

    Bad:

    ```
    names = {"key": "value"}
    nums = [1, 2, 3]

    del names["key"]
    del nums[0]
    del nums[:]
    ```

    Good:

    ```
    names = {"key": "value"}
    nums = [1, 2, 3]

    names.pop("key")
    nums.pop(0)
    nums.clear()
    ```
    """

    name = "no-del"
    code = 131
    categories = ["builtin", "readability"]


def check(node: DelStmt, errors: list[Error]) -> None:
    match node:
        case DelStmt(
            expr=IndexExpr(base=NameExpr(node=Var(type=ty)), index=index)
        ) if str(ty).startswith(("builtins.dict[", "builtins.list[")):
            match index:
                case SliceExpr(begin_index=None, end_index=None):
                    errors.append(
                        ErrorInfo(
                            node.line,
                            node.column,
                            "Replace `del x[:]` with `x.clear()`",
                        )
                    )

                case SliceExpr():
                    pass

                case _:
                    errors.append(
                        ErrorInfo(
                            node.line,
                            node.column,
                            "Replace `del x[y]` with `x.pop(y)`",
                        )
                    )
