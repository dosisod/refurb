from dataclasses import dataclass

from mypy.nodes import CallExpr, MemberExpr, NameExpr, OpExpr, Var

from refurb.checks.common import extract_binary_oper
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
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

    name = "use-startswith-endswith-tuple"
    code = 102
    categories = ["string"]


def check(node: OpExpr, errors: list[Error]) -> None:
    match extract_binary_oper("or", node):
        case (
            CallExpr(
                callee=MemberExpr(
                    expr=NameExpr(node=Var(type=ty)) as lhs, name=lhs_func
                ),
                args=args,
            ),
            CallExpr(callee=MemberExpr(expr=NameExpr() as rhs, name=rhs_func)),
        ) if (
            lhs.fullname == rhs.fullname
            and str(ty) in ("builtins.str", "builtins.bytes")
            and lhs_func == rhs_func
            and lhs_func in ("startswith", "endswith")
            and args
        ):
            errors.append(
                ErrorInfo(
                    args[0].line,
                    args[0].column,
                    msg=f"Replace `x.{lhs_func}(y) or x.{lhs_func}(z)` with `x.{lhs_func}((y, z))`",  # noqa: E501
                )
            )
