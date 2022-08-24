from dataclasses import dataclass

from mypy.nodes import (
    ArgKind,
    Argument,
    CallExpr,
    Decorator,
    FuncDef,
    IntExpr,
    MemberExpr,
    NameExpr,
    OverloadedFuncDef,
    StrExpr,
    SymbolNode,
    TypeInfo,
    Var,
)
from mypy.types import Instance

from refurb.error import Error


@dataclass
class ErrorUseImplicitDefault(Error):
    """
    Don't pass an argument if it is the same as the default value:

    Bad:

    ```
    def greet(name: str = "bob") -> None:
        print(f"Hello {name}")

    greet("bob")

    {}.get("some key", None)
    ```

    Good:

    ```
    def greet(name: str = "bob") -> None:
        print(f"Hello {name}")

    greet()

    {}.get("some key")
    ```
    """

    code = 120
    msg: str = "Don't pass an argument if it is the same as the default value"


NoneNode = NameExpr("None")
NoneNode.fullname = "builtins.None"


BUILTIN_MAPPINGS = {
    "builtins.dict.fromkeys": (..., NoneNode),
    "builtins.dict.get": (..., NoneNode),
    "builtins.dict.setdefault": (..., NoneNode),
    "builtins.round": (..., IntExpr(0)),
    "builtins.input": (StrExpr(""),),
}


def get_full_type_name(node: CallExpr) -> str:
    match node:
        case CallExpr(callee=NameExpr() as name):
            return name.fullname or ""

        case CallExpr(
            callee=MemberExpr(
                expr=NameExpr(
                    node=(
                        Var(type=Instance(type=TypeInfo() as ty))
                        | (TypeInfo() as ty)
                    )
                ),
                name=name,
            ),
        ):
            return f"{ty.fullname}.{name}"

    return ""


def inject_stdlib_defaults(node: CallExpr, args: list[Argument]) -> None:
    if defaults := BUILTIN_MAPPINGS.get(get_full_type_name(node)):
        for default, arg in zip(defaults, args):
            if default == Ellipsis:
                continue

            arg.initializer = default  # type: ignore


def check_func(caller: CallExpr, func: FuncDef, errors: list[Error]) -> None:
    args = list(zip(func.arg_names, func.arguments))

    if isinstance(caller.callee, MemberExpr):
        args.pop(0)

    lookup = dict(args)

    inject_stdlib_defaults(caller, [x[1] for x in args])

    for i, (name, value, kind) in enumerate(
        zip(caller.arg_names, caller.args, caller.arg_kinds)
    ):
        if i >= len(args):
            break

        if kind == ArgKind.ARG_NAMED:
            default = lookup[name].initializer

        elif kind == ArgKind.ARG_POS:
            default = args[i][1].initializer

        else:
            return

        if str(value) == str(default):
            errors.append(ErrorUseImplicitDefault(value.line, value.column))


def check_symbol(
    node: CallExpr, symbol: SymbolNode | None, errors: list[Error]
) -> None:
    match symbol:
        case Decorator(func=FuncDef() as func) | (FuncDef() as func):
            check_func(node, func, errors)

        case OverloadedFuncDef(items=items):
            error_count = len(errors)

            for item in items:
                if len(errors) > error_count:
                    break

                if isinstance(item, Decorator):
                    check_func(node, item.func, errors)

                else:
                    check_func(node, item, errors)

        case _:
            return


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(callee=NameExpr(node=symbol)):
            check_symbol(node, symbol, errors)

        case CallExpr(
            callee=MemberExpr(
                expr=NameExpr(
                    node=(
                        Var(type=Instance(type=TypeInfo() as ty))
                        | (TypeInfo() as ty)
                    )
                ),
                name=name,
            ),
        ) if symbol := ty.names.get(
            name
        ):  # type: ignore
            check_symbol(node, symbol.node, errors)  # type: ignore
