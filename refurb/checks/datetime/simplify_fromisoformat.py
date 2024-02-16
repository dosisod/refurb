from dataclasses import dataclass

from mypy.nodes import (
    CallExpr,
    Expression,
    IndexExpr,
    IntExpr,
    MemberExpr,
    OpExpr,
    RefExpr,
    SliceExpr,
    StrExpr,
    UnaryExpr,
)

from refurb.checks.common import get_mypy_type, is_same_type, stringify
from refurb.error import Error
from refurb.settings import Settings


@dataclass
class ErrorInfo(Error):
    """
    Python 3.11 adds support for parsing UTC timestamps that end with `Z`, thus
    removing the need to strip and append the `+00:00` timezone.

    Bad:

    ```
    date = "2023-02-21T02:23:15Z"

    start_date = datetime.fromisoformat(date.replace("Z", "+00:00"))
    ```

    Good:

    ```
    date = "2023-02-21T02:23:15Z"

    start_date = datetime.fromisoformat(date)
    ```
    """

    name = "simplify-fromisoformat"
    code = 162
    categories = ("datetime", "python311", "readability")


def is_string(node: Expression) -> bool:
    return is_same_type(get_mypy_type(node), str)


def is_zero_offset_timezone(timezone: str) -> bool:
    return timezone.startswith(("+", "-")) and timezone.strip("+-") in {"00:00", "0000", "00"}


def check(node: CallExpr, errors: list[Error], settings: Settings) -> None:
    if settings.get_python_version() < (3, 11):
        return

    match node:
        case CallExpr(
            callee=MemberExpr(expr=RefExpr(fullname="datetime.datetime"), name="fromisoformat"),
            args=[arg],
        ):
            func_name = stringify(node.callee)

            match arg:
                case CallExpr(
                    callee=MemberExpr(expr=date, name="replace"),
                    args=[
                        StrExpr(value="Z"),
                        StrExpr(value=timezone),
                    ],
                ) if is_string(date) and is_zero_offset_timezone(timezone):
                    old = f'{func_name}(x.replace("Z", "{timezone}"))'

                case OpExpr(
                    left=IndexExpr(
                        base=date,
                        index=SliceExpr(
                            begin_index=None,
                            end_index=UnaryExpr(op="-", expr=IntExpr(value=1)),
                            stride=None,
                        ),
                    ),
                    op="+",
                    right=StrExpr(value=timezone),
                ) if is_string(date) and is_zero_offset_timezone(timezone):
                    old = f'{func_name}(x[:-1] + "{timezone}")'

                case OpExpr(
                    left=CallExpr(
                        callee=MemberExpr(expr=date, name="strip" | "rstrip" as str_func_name),
                        args=[StrExpr(value="Z")],
                    ),
                    op="+",
                    right=StrExpr(value=timezone),
                ) if is_string(date) and is_zero_offset_timezone(timezone):
                    old = f'{func_name}(x.{str_func_name}("Z") + "{timezone}")'

                case _:
                    return

            if is_string(date) and is_zero_offset_timezone(timezone):
                errors.append(ErrorInfo.from_node(node, f"Replace `{old}` with `{func_name}(x)`"))
