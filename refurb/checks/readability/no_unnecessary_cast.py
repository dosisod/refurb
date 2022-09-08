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
class ErrorNoUnnecessaryCast(Error):
    """
    Don't cast a variable or literal if it is already of that type. For
    example:

    Bad:

    ```
    name = str("bob")
    num = int(123)
    ```

    Good:

    ```
    name = "bob"
    num = 123
    ```
    """

    code = 123


FUNC_NAMES = {
    "builtins.bool": None,
    "builtins.bytes": BytesExpr,
    "builtins.complex": ComplexExpr,
    "builtins.dict": DictExpr,
    "builtins.float": FloatExpr,
    "builtins.int": IntExpr,
    "builtins.list": ListExpr,
    "builtins.str": StrExpr,
    "builtins.tuple": TupleExpr,
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
            if type(arg) == FUNC_NAMES[fullname]:
                pass

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
                ErrorNoUnnecessaryCast(
                    node.line,
                    node.column,
                    f"Use `x` instead of `{name}(x)`",
                )
            )
