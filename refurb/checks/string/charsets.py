import string
from dataclasses import dataclass

from mypy.nodes import ComparisonExpr, StrExpr

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Python includes some pre-defined charsets such as digits (0-9), upper and
    lower case alpha characters, and so on. You don't have to define them
    yourself, and they are usually more readable.

    Bad:

    ```
    digits = "0123456789"

    if c in digits:
        pass

    if c in "0123456789abcdefABCDEF":
        pass
    ```

    Good:

    ```
    if c in string.digits:
        pass

    if c in string.hexdigits:
        pass
    ```

    Note that when using a literal string, the corresponding `string.xyz` value
    must be exact, but when used in an `in` comparison, the characters can be
    out of order since `in` will compare every character in the string.
    """

    name = "use-string-charsets"
    code = 156
    categories = ["readability", "string"]


_CHARSETS = [
    "ascii_letters",
    "ascii_lowercase",
    "ascii_uppercase",
    "digits",
    "hexdigits",
    "octdigits",
    "printable",
    "punctuation",
    "whitespace",
]

CHARSETS_EXACT = {
    f"string.{name}": getattr(string, name) for name in _CHARSETS
}
CHARSET_PERMUTATIONS = {
    name: frozenset(value) for name, value in CHARSETS_EXACT.items()
}


def format_error(value: str, name: str) -> str:
    # Escape and pretty print control chars, remove surrounding quotes
    value = repr(value)[1:-1].replace("\\x0b", "\\v").replace("\\x0c", "\\f")

    return f"Replace `{value}` with `{name}`"


def check(node: ComparisonExpr | StrExpr, errors: list[Error]) -> None:
    match node:
        case ComparisonExpr(
            operators=["in"], operands=[_, StrExpr(value=value)]
        ):
            value_set = set(value)

            for name, charset in CHARSET_PERMUTATIONS.items():
                if value_set == charset:
                    errors.append(
                        ErrorInfo(
                            node.line,
                            node.column,
                            format_error(value, name),
                        )
                    )

        case StrExpr(value=value):
            for name, charset in CHARSETS_EXACT.items():
                if value == charset:  # type: ignore
                    errors.append(
                        ErrorInfo(
                            node.line,
                            node.column,
                            format_error(value, name),
                        )
                    )
