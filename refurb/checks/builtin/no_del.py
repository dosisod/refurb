from dataclasses import dataclass

from mypy.nodes import DelStmt, IndexExpr, NameExpr, SliceExpr, Var

from refurb.checks.common import stringify
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    The `del` statement is commonly used for popping single elements from dicts
    and lists, though a slice can be used to remove a range of elements
    instead. When removing all elements via a slice, use the faster and more
    succinct `.clear()` method instead.

    Bad:

    ```
    names = {"key": "value"}
    nums = [1, 2, 3]

    del names[:]
    del nums[:]
    ```

    Good:

    ```
    names = {"key": "value"}
    nums = [1, 2, 3]

    names.clear()
    nums.clear()
    ```
    """

    name = "no-del"
    code = 131
    categories = ("builtin", "readability")


def check(node: DelStmt, errors: list[Error]) -> None:
    match node:
        case DelStmt(expr=IndexExpr(base=NameExpr(node=Var(type=ty)) as expr, index=index)) if str(
            ty
        ).startswith(("builtins.dict[", "builtins.list[")):
            match index:
                case SliceExpr(begin_index=None, end_index=None):
                    expr = stringify(expr)  # type: ignore

                    msg = f"Replace `del {expr}[:]` with `{expr}.clear()`"

                    errors.append(ErrorInfo.from_node(node, msg))
