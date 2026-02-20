from dataclasses import dataclass

from mypy.nodes import AssignmentStmt, CallExpr, Expression, IndexExpr, MemberExpr

from refurb.checks.common import (
    get_mypy_type,
    is_equivalent,
    is_subclass,
)
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    When setting a dict value if the key is not present, instead of
    using `.get()` with assignment, use `.setdefault()`:

    Bad:

    ```
    d[key] = d.get(key, default)
    d[key] = d.get(key)
    ```

    Good:

    ```
    d.setdefault(key, default)
    d.setdefault(key)
    ```
    """

    code = 193
    name = "use-setdefault"
    categories = ("builtin", "readability")
    msg: str = "Replace `d[key] = d.get(key, default)` with `d.setdefault(key, default)`"


def _is_mutable_mapping(expr: Expression) -> bool:
    return is_subclass(get_mypy_type(expr), "typing.MutableMapping")


def check(node: AssignmentStmt, errors: list[Error]) -> None:
    match node:
        case AssignmentStmt(
            lvalues=[IndexExpr(base=dict_expr, index=key_expr)],
            rvalue=CallExpr(
                callee=MemberExpr(expr=get_dict_expr, name="get"),
                args=[get_key_expr, *_],
            ),
        ) if (
            _is_mutable_mapping(dict_expr)
            and is_equivalent(dict_expr, get_dict_expr)
            and is_equivalent(key_expr, get_key_expr)
        ):
            errors.append(ErrorInfo.from_node(node))
