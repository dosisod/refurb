from dataclasses import dataclass

from mypy.nodes import CallExpr, ComparisonExpr, NameExpr

from refurb.checks.common import is_type_none_call, stringify
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Don't use `type(None)` to check if the type of an object is `None`, use an
    `is` comparison instead.

    Bad:

    ```
    x = 123

    if type(x) is type(None):
        pass
    ```

    Good:

    ```
    x = 123

    if x is None:
        pass
    ```
    """

    name = "no-is-type-none"
    code = 169
    categories = ("pythonic", "readability")


def check(node: ComparisonExpr, errors: list[Error]) -> None:
    match node:
        case ComparisonExpr(
            operators=["is" | "is not" | "==" | "!=" as oper],
            operands=[
                CallExpr(callee=NameExpr(fullname="builtins.type"), args=[arg]),
                rhs,
            ],
        ) if is_type_none_call(rhs):
            new = "is" if oper in {"is", "=="} else "is not"

            expr = stringify(arg)

            msg = f"Replace `type({expr}) {oper} type(None)` with `{expr} {new} None`"

            errors.append(ErrorInfo.from_node(node, msg))
