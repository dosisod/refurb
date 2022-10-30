from dataclasses import dataclass

from mypy.nodes import MypyFile

from refurb.error import Error
from refurb.settings import Settings


@dataclass
class ErrorInfo(Error):
    """
    TODO: fill this in

    Bad:

    ```
    # TODO: fill this in
    ```

    Good:

    ```
    # TODO: fill this in
    ```
    """

    prefix = "XYZ"
    code = 103
    msg: str = "Your message here"


def check(node: MypyFile, errors: list[Error], settings: Settings) -> None:
    msg = f"Files being checked: {settings.files}"

    errors.append(ErrorInfo(node.line, node.column, msg))
