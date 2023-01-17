from dataclasses import dataclass

from mypy.nodes import (
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

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Don't cast a variable or literal if it is already of that type. This
    usually is the result of not realizing a type is already the type you want,
    or artifacts of some debugging code. One example of where this might be
    intentional is when using container types like `dict` or `list`, which
    will create a shadow copy. If that is the case, it might be preferable
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
    categories = ["readability"]


FUNC_NAMES = {
    "builtins.bool": (None, "x"),
    "builtins.bytes": (BytesExpr, "x"),
    "builtins.complex": (ComplexExpr, "x"),
    "builtins.dict": (DictExpr, "x.copy()"),
    "builtins.float": (FloatExpr, "x"),
    "builtins.int": (IntExpr, "x"),
    "builtins.list": (ListExpr, "x.copy()"),
    "builtins.str": (StrExpr, "x"),
    "builtins.tuple": (TupleExpr, "x"),
}


def is_boolean_literal(node: Expression) -> bool:
    return isinstance(node, NameExpr) and node.fullname in (
        "builtins.True",
        "builtins.False",
    )


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=NameExpr(fullname=fullname, name=name),
            args=[arg],
        ) if fullname in FUNC_NAMES:
            node_type, msg = FUNC_NAMES[fullname]

            if type(arg) == node_type:
                if isinstance(arg, DictExpr | ListExpr):
                    msg = "x"

            elif is_boolean_literal(arg) and name == "bool":
                pass

            else:
                match arg:
                    case NameExpr(node=Var(type=ty)) if (
                        str(ty).startswith(fullname)
                        or (str(ty).startswith("Tuple") and name == "tuple")
                    ):
                        pass

                    case _:
                        return

            errors.append(
                ErrorInfo(
                    node.line,
                    node.column,
                    f"Replace `{name}(x)` with `{msg}`",
                )
            )
