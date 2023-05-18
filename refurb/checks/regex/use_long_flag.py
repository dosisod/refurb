from dataclasses import dataclass

from mypy.nodes import MemberExpr, NameExpr, RefExpr

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Regex operations can be changed using flags such as `re.I`, which will make
    the regex case-insensitive. These single-character flag names can be harder
    to read/remember, and should be replaced with the longer aliases so that
    they are more descriptive.

    Bad:

    ```
    if re.match("^hello", "hello world", re.I):
        pass
    ```

    Good:

    ```
    if re.match("^hello", "hello world", re.IGNORECASE):
        pass
    ```
    """

    name = "use-long-regex-flag"
    code = 167
    categories = ("readability", "regex")


SHORT_TO_LONG_FLAG = {
    "re.A": "re.ASCII",
    "re.I": "re.IGNORECASE",
    "re.L": "re.LOCALE",
    "re.M": "re.MULTILINE",
    "re.S": "re.DOTALL",
    "re.T": "re.TEMPLATE",
    "re.U": "re.UNICODE",
    "re.X": "re.VERBOSE",
}


def check(node: NameExpr | MemberExpr, errors: list[Error]) -> None:
    match node:
        case RefExpr(fullname=fullname):
            if long_name := SHORT_TO_LONG_FLAG.get(fullname):
                errors.append(
                    ErrorInfo.from_node(
                        node, f"Replace `{fullname}` with `{long_name}`"
                    )
                )
