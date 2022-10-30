from dataclasses import dataclass

from mypy.nodes import CallExpr, NameExpr, OpExpr

from refurb.checks.common import extract_binary_oper
from refurb.error import Error
from refurb.settings import Settings


@dataclass
class ErrorInfo(Error):
    """
    `isinstance()` and `issubclass()` both take tuple arguments, so instead of
    calling them multiple times for the same object, you can check all of them
    at once:

    Bad:

    ```
    if isinstance(num, float) or isinstance(num, int):
        pass
    ```

    Good:

    ```
    if isinstance(num, (float, int)):
        pass
    ```

    Note: In Python 3.10+, you can also pass type unions as the second param to
    these functions:

    ```
    if isinstance(num, float | int):
        pass
    ```
    """

    code = 121


def check(node: OpExpr, errors: list[Error], settings: Settings) -> None:
    exprs = extract_binary_oper("or", node)

    # TODO: remove when next mypy version is released
    if not exprs:
        return

    match exprs:
        case (
            CallExpr(callee=NameExpr() as lhs, args=lhs_args),
            CallExpr(callee=NameExpr() as rhs, args=rhs_args),
        ) if (
            lhs.fullname == rhs.fullname
            and lhs.fullname in ("builtins.isinstance", "builtins.issubclass")
            and len(lhs_args) == 2
            and str(lhs_args[0]) == str(rhs_args[0])
        ):
            if settings.python_version and settings.python_version >= (3, 10):
                type_args = "y | z"
            else:
                type_args = "(y, z)"

            errors.append(
                ErrorInfo(
                    lhs_args[1].line,
                    lhs_args[1].column,
                    msg=f"Replace `{lhs.name}(x, y) or {lhs.name}(x, z)` with `{lhs.name}(x, {type_args})`",  # noqa: E501
                )
            )
