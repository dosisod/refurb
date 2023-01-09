from dataclasses import dataclass
from typing import Iterator

from mypy.nodes import (
    ArgKind,
    Argument,
    CallExpr,
    Decorator,
    Expression,
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

from refurb.checks.common import is_equivalent
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
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

    name = "use-implicit-default"
    enabled = False
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
    "builtins.int": (..., IntExpr(10)),
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


ZippedArg = tuple[str | None, Expression, ArgKind]


def strip_caller_var_args(
    start: int, args: Iterator[ZippedArg]
) -> Iterator[ZippedArg]:
    for i, arg in enumerate(args):
        if i < start:
            continue

        if arg[2] == ArgKind.ARG_NAMED:
            yield arg


def check_func(caller: CallExpr, func: FuncDef, errors: list[Error]) -> None:
    args = list(zip(func.arg_names, func.arguments))

    if (
        isinstance(caller.callee, MemberExpr)
        and args
        and func.arg_names[0] in ("self", "cls")
    ):
        args.pop(0)

    lookup = dict(args)

    inject_stdlib_defaults(caller, [x[1] for x in args])

    caller_args = zip(caller.arg_names, caller.args, caller.arg_kinds)

    for i, arg in enumerate(args):
        if arg[1].kind == ArgKind.ARG_STAR:
            caller_args = strip_caller_var_args(i, caller_args)  # type: ignore

    for i, (name, value, kind) in enumerate(caller_args):
        if i >= len(args):
            break

        if kind == ArgKind.ARG_NAMED:
            try:
                default = lookup[name].initializer
            except KeyError:
                continue

        elif kind == ArgKind.ARG_POS:
            default = args[i][1].initializer

        else:
            return  # pragma: no cover

        if default and is_equivalent(value, default):
            errors.append(ErrorInfo(value.line, value.column))


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

            if symbol.impl:
                if isinstance(symbol.impl, FuncDef):
                    check_func(node, symbol.impl, errors)

                else:
                    check_func(node, symbol.impl.func, errors)

        case TypeInfo():
            for func_name in ("__new__", "__init__"):
                if new_symbol := symbol.names.get(func_name):
                    if new_symbol.node:
                        check_symbol(node, new_symbol.node, errors)


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(callee=NameExpr(node=symbol)):
            check_symbol(node, symbol, errors)

        # TODO: find a way to make this look nicer
        case CallExpr(
            callee=MemberExpr(
                expr=(
                    NameExpr(
                        node=(
                            Var(type=Instance(type=TypeInfo() as ty))
                            | (TypeInfo() as ty)
                        )
                    )
                    | CallExpr(
                        callee=NameExpr(
                            node=(
                                Var(type=Instance(type=TypeInfo() as ty))
                                | (TypeInfo() as ty)
                            )
                        )
                    )
                ),
                name=name,
            ),
        ) if symbol := ty.names.get(
            name
        ):  # type: ignore
            check_symbol(node, symbol.node, errors)  # type: ignore
