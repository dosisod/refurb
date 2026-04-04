from collections.abc import Iterator
from dataclasses import dataclass

from mypy.nodes import (
    ArgKind,
    Argument,
    AssignmentStmt,
    CallExpr,
    Decorator,
    Expression,
    FuncDef,
    IntExpr,
    MemberExpr,
    MypyFile,
    NameExpr,
    OverloadedFuncDef,
    StrExpr,
    SymbolNode,
    TypeInfo,
    Var,
)
from mypy.types import Instance

from refurb.checks.common import extract_typeinfo, is_equivalent, is_subclass
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

    This check also works with Pydantic BaseModel classes:

    Bad:

    ```
    from pydantic import BaseModel, Field

    class User(BaseModel):
        name: str = "anonymous"
        role: str = Field(default="user")

    User(name="anonymous")  # Same as default
    User(role="user")  # Same as default
    ```

    Good:

    ```
    User()  # Uses defaults
    User(name="alice")  # Different from default
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
                    node=(Var(type=Instance(type=TypeInfo() as ty)) | (TypeInfo() as ty))
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


def strip_caller_var_args(start: int, args: Iterator[ZippedArg]) -> Iterator[ZippedArg]:
    for i, arg in enumerate(args):
        if i < start:
            continue

        if arg[2] == ArgKind.ARG_NAMED:
            yield arg


def check_func(caller: CallExpr, func: FuncDef, errors: list[Error]) -> None:
    args = list(zip(func.arg_names, func.arguments))

    if isinstance(caller.callee, MemberExpr) and args and func.arg_names[0] in {"self", "cls"}:
        args.pop(0)

    lookup = dict(args)

    inject_stdlib_defaults(caller, [x[1] for x in args])

    caller_args = zip(caller.arg_names, caller.args, caller.arg_kinds)

    for i, arg in enumerate(args):
        if arg[1].kind == ArgKind.ARG_STAR:
            caller_args = strip_caller_var_args(i, caller_args)  # type: ignore

    temp_errors: list[Error] = []

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
            temp_errors.append(ErrorInfo.from_node(value))

        elif kind == ArgKind.ARG_POS:
            # Since this arg is not a default value and cannot be deleted,
            # deleting previous default args would cause this arg to become
            # misaligned. If this was a kwarg it wouldn't be an issue because
            # the position would not be affected during deletion.
            temp_errors = []

    errors.extend(temp_errors)


def check_symbol(node: CallExpr, symbol: SymbolNode | None, errors: list[Error]) -> None:
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
            # Check if this is a Pydantic BaseModel
            if is_pydantic_model(symbol):
                check_pydantic_model(node, symbol, errors)
            else:
                for func_name in ("__new__", "__init__"):
                    if new_symbol := symbol.names.get(func_name):
                        assert new_symbol.node

                        check_symbol(node, new_symbol.node, errors)


PYDANTIC_BASE_MODEL_NAMES = frozenset({
    "pydantic.BaseModel",
    "pydantic.main.BaseModel",
    "pydantic.v1.BaseModel",
    "pydantic.v1.main.BaseModel",
})

PYDANTIC_FIELD_NAMES = frozenset({
    "pydantic.Field",
    "pydantic.fields.Field",
    "pydantic.v1.Field",
    "pydantic.v1.fields.Field",
})


def is_pydantic_model(ty: TypeInfo) -> bool:
    """Check if a TypeInfo is a subclass of pydantic.BaseModel."""
    for base in ty.mro:
        if base.fullname in PYDANTIC_BASE_MODEL_NAMES:
            return True
    return False


def get_pydantic_field_default(var: Var, ty: TypeInfo) -> Expression | None:
    """Extract the default value from a Pydantic field variable."""
    # We need to find the assignment statement in the class definition
    # that defines this field
    defn = ty.defn
    
    for stmt in defn.defs.body:
        if isinstance(stmt, AssignmentStmt):
            for lval in stmt.lvalues:
                if isinstance(lval, NameExpr) and lval.name == var.name:
                    rvalue = stmt.rvalue
                    
                    # Case 1: Simple default value (e.g., arg: int = 1)
                    if not isinstance(rvalue, CallExpr):
                        return rvalue
                    
                    # Case 2: Field() call (e.g., arg: int = Field(default=1))
                    if isinstance(rvalue, CallExpr):
                        callee = rvalue.callee
                        if isinstance(callee, NameExpr):
                            if callee.fullname in PYDANTIC_FIELD_NAMES:
                                # Look for 'default' argument
                                for arg_name, arg in zip(rvalue.arg_names, rvalue.args):
                                    if arg_name == "default":
                                        return arg
                                # Also check positional first argument as default
                                if rvalue.args and rvalue.arg_names and rvalue.arg_names[0] is None:
                                    return rvalue.args[0]
    
    return None


def check_pydantic_model(node: CallExpr, ty: TypeInfo, errors: list[Error]) -> None:
    """Check Pydantic BaseModel instantiation for redundant default arguments."""
    # Build a lookup of field names to their default values
    field_defaults: dict[str, Expression] = {}
    
    # Get the class definition's body to find field assignments
    for name, symbol in ty.names.items():
        if isinstance(symbol.node, Var):
            var = symbol.node
            # Skip private/dunder attributes
            if name.startswith("_"):
                continue
            
            # Only check fields that are initialized in the class
            if not var.is_initialized_in_class:
                continue
            
            default = get_pydantic_field_default(var, ty)
            if default is not None:
                field_defaults[name] = default
    
    if not field_defaults:
        return
    
    # Check the call arguments against the field defaults
    temp_errors: list[Error] = []
    
    for i, (name, value, kind) in enumerate(zip(node.arg_names, node.args, node.arg_kinds)):
        if kind == ArgKind.ARG_NAMED:
            if name in field_defaults:
                default = field_defaults[name]
                if is_equivalent(value, default):
                    temp_errors.append(ErrorInfo.from_node(value))
        elif kind == ArgKind.ARG_POS:
            # For positional args, we need to match by position
            # Get the field names in order (this is tricky without __init__ signature)
            # For now, we'll skip positional args for Pydantic models
            # since field order may not match __init__ order
            pass
    
    errors.extend(temp_errors)


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(callee=NameExpr(node=symbol)):
            check_symbol(node, symbol, errors)

        # TODO: find a way to make this look nicer
        case CallExpr(
            callee=MemberExpr(
                expr=(
                    NameExpr(node=(Var(type=Instance(type=TypeInfo() as ty)) | (TypeInfo() as ty)))
                    | CallExpr(
                        callee=NameExpr(
                            node=(Var(type=Instance(type=TypeInfo() as ty)) | (TypeInfo() as ty))
                        )
                    )
                ),
                name=name,
            ),
        ) if symbol := ty.names.get(
            name
        ):  # type: ignore
            check_symbol(node, symbol.node, errors)  # type: ignore
