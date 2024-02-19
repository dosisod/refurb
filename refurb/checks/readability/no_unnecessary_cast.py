from dataclasses import dataclass

from mypy.nodes import ArgKind, CallExpr, NameExpr

from refurb.checks.common import get_mypy_type, is_same_type, stringify
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Don't cast a variable or literal if it is already of that type. This
    usually is the result of not realizing a type is already the type you want,
    or artifacts of some debugging code. One example of where this might be
    intentional is when using container types like `dict` or `list`, which
    will create a shallow copy. If that is the case, it might be preferable
    to use `.copy()` instead, since it makes it more explicit that a copy
    is taking place.

    Examples:

    Bad:

    ```
    name = str("bob")
    num = int(123)

    ages = {"bob": 123}
    copy = dict(ages)
    ```

    Good:

    ```
    name = "bob"
    num = 123

    ages = {"bob": 123}
    copy = ages.copy()
    ```
    """

    name = "no-redundant-cast"
    code = 123
    categories = ("readability",)


FUNC_NAME_MAPPING = {
    "builtins.bool": ("", bool),
    "builtins.bytes": ("", bytes),
    "builtins.complex": ("", complex),
    "builtins.dict": (".copy()", dict, "os._Environ"),
    "builtins.float": ("", float),
    "builtins.int": ("", int),
    "builtins.list": (".copy()", list),
    "builtins.set": (".copy()", set),
    "builtins.str": ("", str),
    "builtins.tuple": ("", tuple),
}


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=NameExpr(fullname=fullname, name=name),
            args=[arg],
            arg_kinds=[ArgKind.ARG_POS],
        ) if found := FUNC_NAME_MAPPING.get(fullname):
            suffix, *expected_types = found

            if not is_same_type(get_mypy_type(arg), *expected_types):
                return

            expr = stringify(arg)

            msg = f"Replace `{name}({stringify(arg)})` with `{expr}{suffix}`"

            errors.append(ErrorInfo.from_node(node, msg))
