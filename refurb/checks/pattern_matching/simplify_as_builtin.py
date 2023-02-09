from dataclasses import dataclass

from mypy.nodes import NameExpr
from mypy.patterns import AsPattern, ClassPattern

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    When pattern matching builtin classes such as `int()` and `str()`, don't
    use an `as` pattern to bind to the value, since the most common builtin
    classes can use positional patterns instead.

    Bad:

    ```
    match x:
        case str() as name:
            print(f"Hello {name}")
    ```

    Good:

    ```
    match x:
        case str(name):
            print(f"Hello {name}")
    ```
    """

    name = "simplify-as-pattern-with-builtin"
    code = 158
    categories = ["pattern-matching", "readability"]


BUILTIN_PATTERN_CLASSES = (
    "builtins.bool",
    "builtins.bytearray",
    "builtins.bytes",
    "builtins.dict",
    "builtins.float",
    "builtins.frozenset",
    "builtins.int",
    "builtins.list",
    "builtins.set",
    "builtins.str",
    "builtins.tuple",
)


def check(node: AsPattern, errors: list[Error]) -> None:
    match node:
        case AsPattern(
            pattern=ClassPattern(
                class_ref=NameExpr(name=name, fullname=fullname),
                positionals=[],
                keyword_keys=[],
                keyword_values=[],
            )
        ) if fullname in BUILTIN_PATTERN_CLASSES:
            errors.append(
                ErrorInfo(
                    node.line,
                    node.column,
                    f"Replace `{name}() as x` with `{name}(x)`",
                )
            )
