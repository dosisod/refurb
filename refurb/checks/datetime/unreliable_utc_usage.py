from dataclasses import dataclass
from typing import Final

from mypy.nodes import CallExpr, MemberExpr, NameExpr

from refurb.error import Error
from refurb.settings import Settings


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


def check(node: CallExpr, errors: list[Error], settings: Settings) -> None:
    match node:
        case CallExpr(
            callee=MemberExpr(
                expr=NameExpr(fullname="datetime.datetime"),
            ) as func,
        ) if func.name in {
            "utcnow",
            "utcfromtimestamp",
        }:
            pars, replaced = _replacements[func.name]
            errors.append(
                ErrorInfo.from_node(
                    node,
                    f"Replace `{func.name}{pars}` with `{replaced}`",
                )
            )
