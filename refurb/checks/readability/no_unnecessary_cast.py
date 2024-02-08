from dataclasses import dataclass

from mypy.nodes import (
    ArgKind,
    BytesExpr,
    CallExpr,
    ComplexExpr,
    DictExpr,
    Expression,
    FloatExpr,
    IntExpr,
    ListExpr,
    NameExpr,
    StrExpr,
    TupleExpr,
    Var,
)

from refurb.checks.common import is_same_type, stringify
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
    "builtins.bool": (bool, None, ""),
    "builtins.bytes": (bytes, BytesExpr, ""),
    "builtins.complex": (complex, ComplexExpr, ""),
    "builtins.dict": (dict, DictExpr, ".copy()"),
    "builtins.float": (float, FloatExpr, ""),
    "builtins.int": (int, IntExpr, ""),
    "builtins.list": (list, ListExpr, ".copy()"),
    "builtins.str": (str, StrExpr, ""),
    "builtins.tuple": (tuple, TupleExpr, ""),
}


def is_boolean_literal(node: Expression) -> bool:
    return isinstance(node, NameExpr) and node.fullname in {"builtins.True", "builtins.False"}


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=NameExpr(fullname=fullname, name=name),
            args=[arg],
            arg_kinds=[ArgKind.ARG_POS],
        ) if found := FUNC_NAME_MAPPING.get(fullname):
            expected_type, node_type, suffix = found

            if (type(arg) == node_type) or (is_boolean_literal(arg) and name == "bool"):
                pass

            else:
                match arg:
                    case NameExpr(node=Var(type=ty)) if is_same_type(ty, expected_type):
                        pass

                    case _:
                        return

            expr = stringify(arg)

            msg = f"Replace `{name}({stringify(arg)})` with `{expr}{suffix}`"

            errors.append(ErrorInfo.from_node(node, msg))
