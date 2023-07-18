from dataclasses import dataclass
from typing import Final

from mypy.nodes import CallExpr, MemberExpr, RefExpr

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Because naive `datetime` objects are treated by many `datetime` methods
    as local times, it is preferred to use aware datetimes to represent times
    in UTC.

    This check affects `datetime.utcnow` and `datetime.utcfromtimestamp`.

    Bad:

    ```
    from datetime import datetime

    now = datetime.utcnow()
    past_date = datetime.utcfromtimestamp(some_timestamp)
    ```

    Good:

    ```
    from datetime import datetime, timezone

    datetime.now(timezone.utc)
    datetime.fromtimestamp(some_timestamp, tz=timezone.utc)
    ```
    """

    name = "unreliable-utc-usage"
    code = 176
    categories = ("datetime",)


_replacements: Final = {
    "utcnow": ("()", "now(tz=timezone.utc)"),
    "utcfromtimestamp": ("(...)", "fromtimestamp(..., tz=timezone.utc)"),
}


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=MemberExpr(
                expr=RefExpr(fullname="datetime.datetime"),
            ) as func,
        ) if replacements := _replacements.get(func.name):
            parens, replaced = replacements
            errors.append(
                ErrorInfo.from_node(
                    node,
                    f"Replace `{func.name}{parens}` with `{replaced}`",
                )
            )
