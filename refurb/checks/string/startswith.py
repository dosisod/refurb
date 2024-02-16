from dataclasses import dataclass

from mypy.nodes import CallExpr, Expression, MemberExpr, OpExpr, UnaryExpr

from refurb.checks.common import extract_binary_oper, get_mypy_type, is_equivalent, is_same_type
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    `startswith()` and `endswith()` both take a tuple, so instead of calling
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
    categories = ("string",)


def are_startswith_or_endswith_calls(
    lhs: Expression, rhs: Expression
) -> tuple[str, Expression] | None:
    match lhs, rhs:
        case (
            CallExpr(callee=MemberExpr(expr=lhs, name=lhs_func), args=[first_arg]),
            CallExpr(callee=MemberExpr(expr=rhs, name=rhs_func), args=[_]),
        ) if (
            is_equivalent(lhs, rhs)
            and is_same_type(get_mypy_type(lhs), str, bytes)
            and lhs_func == rhs_func
            and lhs_func in {"startswith", "endswith"}
        ):
            return lhs_func, first_arg

    return None


def check(node: OpExpr, errors: list[Error]) -> None:
    match extract_binary_oper("or", node):
        case (lhs, rhs) if data := are_startswith_or_endswith_calls(lhs, rhs):
            func, arg = data

            old = f"x.{func}(y) or x.{func}(z)"
            new = f"x.{func}((y, z))"

            errors.append(ErrorInfo.from_node(arg, msg=f"Replace `{old}` with `{new}`"))

    match extract_binary_oper("and", node):
        case (
            UnaryExpr(op="not", expr=lhs),
            UnaryExpr(op="not", expr=rhs),
        ) if data := are_startswith_or_endswith_calls(lhs, rhs):
            func, arg = data

            old = f"not x.{func}(y) and not x.{func}(z)"
            new = f"not x.{func}((y, z))"

            errors.append(ErrorInfo.from_node(arg, msg=f"Replace `{old}` with `{new}`"))
