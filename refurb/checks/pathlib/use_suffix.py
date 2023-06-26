import re
from dataclasses import dataclass

from mypy.nodes import CallExpr, MemberExpr, StrExpr

from refurb.checks.pathlib.util import is_pathlike
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    When checking the file extension for a pathlib object don't call
    `endswith()` on the `name` field, directly check against `suffix` instead.

    Bad:

    ```
    from pathlib import Path

    def is_markdown_file(file: Path) -> bool:
        return file.name.endswith(".md")
    ```

    Good:

    ```
    from pathlib import Path

    def is_markdown_file(file: Path) -> bool:
        return file.suffix == ".md"
    ```

    Note: The `suffix` field will only contain the last file extension, so
    don't use `suffix` if you are checking for an extension like `.tar.gz`.
    Refurb won't warn in those cases, but it is good to remember in case you
    plan to use this in other places.
    """

    enabled = False
    name = "use-suffix"
    code = 172
    categories = ("pathlib",)


FILE_EXTENSION = re.compile(r"^\.[a-zA-Z0-9_-]+$")


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=MemberExpr(
                expr=MemberExpr(
                    expr=file,
                    name="name",
                ),
                name="endswith",
            ),
            args=[StrExpr(value=suffix)],
        ) if FILE_EXTENSION.match(suffix) and is_pathlike(file):
            old = f'x.name.endswith("{suffix}")'
            new = f'x.suffix == "{suffix}"'

            errors.append(
                ErrorInfo.from_node(node, f"Replace `{old}` with `{new}`")
            )
