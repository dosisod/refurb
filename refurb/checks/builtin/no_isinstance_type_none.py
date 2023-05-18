from dataclasses import dataclass

from mypy.nodes import CallExpr, Expression, NameExpr, OpExpr, TupleExpr

from refurb.checks.common import is_type_none_call
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Checking if an object is `None` using `isinstance()` is un-pythonic: use an
    `is` comparison instead.

    Bad:

    ```
    x = 123

    if isinstance(x, type(None)):
        pass
    ```

    Good:

    ```
    x = 123

    if x is None:
        pass
    ```
    """

    name = "no-isinstance-type-none"
    code = 168
    categories = ("pythonic", "readability")


def get_type_none_index(node: Expression, index: int = 0) -> int:
    match node:
        case _ if is_type_none_call(node):
            return index

        case OpExpr(op="|"):
            lhs_index = get_type_none_index(node.left, index)

            if lhs_index != -1:
                return lhs_index

            return get_type_none_index(node.right, index + 1)

    return -1


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=NameExpr(fullname="builtins.isinstance"),
            args=[_, ty],
        ):
            match ty:
                case _ if is_type_none_call(ty):
                    msg = "Replace `isinstance(x, type(None))` with `x is None`"  # noqa: E501

                    errors.append(ErrorInfo.from_node(node, msg))

                    return

                case OpExpr(op="|"):
                    type_none_index = get_type_none_index(ty)

                    if type_none_index == -1:
                        return

                    if type_none_index == 0:
                        types = "type(None) | ..."
                    else:
                        types = "... | type(None)"

                case TupleExpr(items=items):
                    for i, item in enumerate(items):
                        if is_type_none_call(item):
                            if i == 0:
                                types = "(type(None), ...)"
                            else:
                                types = "(..., type(None))"

                            break

                    else:
                        return

                case _:
                    return

            msg = f"Replace `isinstance(x, {types})` with `x is None or isinstance(x, ...)`"  # noqa: E501

            errors.append(ErrorInfo.from_node(node, msg))
