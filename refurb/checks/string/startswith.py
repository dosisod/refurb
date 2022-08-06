from dataclasses import dataclass
from typing import ClassVar

from mypy.nodes import CallExpr, MemberExpr, NameExpr, OpExpr, Var

from refurb.error import Error


@dataclass
class ErrorUseStartswithTuple(Error):
    """
    `startswith()` and `endswith()` both takes a tuple, so instead of calling
    `startswith()` multiple times on the same string, you can check them all
    at once:

    Bad:

    ```
    name = "bob"
    if name.startswith("b") or name.startswith("B"):
        pass
    ```

    Good:

    ```
    name = "bob"
    if name.startswith(("b", "B")):
        pass
    ```
    """

    code: ClassVar[int] = 102


def check(node: OpExpr, errors: list[Error]) -> None:
    match node:
        case OpExpr(
            op="or",
            left=CallExpr(
                callee=MemberExpr(
                    expr=NameExpr(node=Var(type=ty)) as lhs, name=lhs_func
                )
            ),
            right=CallExpr(
                callee=MemberExpr(expr=NameExpr() as rhs, name=rhs_func)
            ),
        ) if (
            lhs.fullname == rhs.fullname
            and str(ty) in ("builtins.str", "builtins.bytes")
            and lhs_func == rhs_func
            and lhs_func in ("startswith", "endswith")
        ):
            errors.append(
                ErrorUseStartswithTuple(
                    node.line,
                    node.column,
                    msg=f"Replace `x.{lhs_func}(y) or x.{lhs_func}(z)` with `x.{lhs_func}((y, z))`",  # noqa: E501
                )
            )
