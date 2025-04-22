from collections.abc import Callable
from itertools import chain, combinations
from typing import Any, TypeGuard

from mypy.nodes import (
    ArgKind,
    AssignmentExpr,
    AssignmentStmt,
    AwaitExpr,
    Block,
    BytesExpr,
    CallExpr,
    CastExpr,
    ComparisonExpr,
    ComplexExpr,
    ConditionalExpr,
    DelStmt,
    DictExpr,
    DictionaryComprehension,
    Expression,
    ExpressionStmt,
    FloatExpr,
    ForStmt,
    FuncDef,
    GeneratorExpr,
    IfStmt,
    IndexExpr,
    IntExpr,
    LambdaExpr,
    ListExpr,
    MemberExpr,
    MypyFile,
    NameExpr,
    Node,
    OpExpr,
    ReturnStmt,
    SetExpr,
    SliceExpr,
    StarExpr,
    Statement,
    StrExpr,
    SymbolNode,
    TupleExpr,
    TypeAlias,
    TypeInfo,
    UnaryExpr,
    Var,
)
from mypy.types import AnyType, CallableType, Instance, TupleType, Type, TypeAliasType

from refurb import types
from refurb.error import Error
from refurb.visitor import TraverserVisitor


def extract_binary_oper(oper: str, node: OpExpr) -> tuple[Expression, Expression] | None:
    match node:
        case OpExpr(
            op=op,
            left=lhs,
            right=rhs,
        ) if op == oper:
            match rhs:
                case OpExpr(op=op, left=rhs) if op == oper:
                    return lhs, rhs

                case OpExpr():
                    return None

                case Expression():
                    return lhs, rhs

    return None


def check_block_like(
    func: Callable[[list[Statement], list[Error]], None],
    node: Block | MypyFile,
    errors: list[Error],
) -> None:
    match node:
        case Block():
            func(node.body, errors)

        case MypyFile():
            func(node.defs, errors)


def check_for_loop_like(
    func: Callable[[Node, Node, list[Node], list[Error]], None],
    node: ForStmt | GeneratorExpr | DictionaryComprehension,
    errors: list[Error],
) -> None:
    match node:
        case ForStmt(index=index, expr=expr):
            func(index, expr, [node.body], errors)

        case GeneratorExpr(
            indices=[index],
            sequences=[expr],
            condlists=condlists,
        ):
            func(
                index,
                expr,
                list(chain([node.left_expr], *condlists)),
                errors,
            )

        case DictionaryComprehension(
            indices=[index],
            sequences=[expr],
            condlists=condlists,
        ):
            func(
                index,
                expr,
                list(chain([node.key, node.value], *condlists)),
                errors,
            )


def unmangle_name(name: str | None) -> str:
    return (name or "").rstrip("'*")


def is_equivalent(lhs: Node | None, rhs: Node | None) -> bool:
    match (lhs, rhs):
        case None, None:
            return True

        case NameExpr() as lhs, NameExpr() as rhs:
            return unmangle_name(lhs.fullname) == unmangle_name(rhs.fullname)

        case MemberExpr() as lhs, MemberExpr() as rhs:
            return (
                lhs.name == rhs.name
                and unmangle_name(lhs.fullname) == unmangle_name(rhs.fullname)
                and is_equivalent(lhs.expr, rhs.expr)
            )

        case IndexExpr() as lhs, IndexExpr() as rhs:
            return is_equivalent(lhs.base, rhs.base) and is_equivalent(lhs.index, rhs.index)

        case CallExpr() as lhs, CallExpr() as rhs:
            return (
                is_equivalent(lhs.callee, rhs.callee)
                and all(map(is_equivalent, lhs.args, rhs.args))
                and lhs.arg_kinds == rhs.arg_kinds
                and lhs.arg_names == rhs.arg_names
            )

        case (
            (ListExpr() as lhs, ListExpr() as rhs)
            | (TupleExpr() as lhs, TupleExpr() as rhs)
            | (SetExpr() as lhs, SetExpr() as rhs)
        ):
            return len(lhs.items) == len(rhs.items) and all(  # type: ignore
                map(is_equivalent, lhs.items, rhs.items)  # type: ignore
            )

        case DictExpr() as lhs, DictExpr() as rhs:
            return len(lhs.items) == len(rhs.items) and all(
                is_equivalent(lhs_item[0], rhs_item[0]) and is_equivalent(lhs_item[1], rhs_item[1])
                for lhs_item, rhs_item in zip(lhs.items, rhs.items)
            )

        case StarExpr() as lhs, StarExpr() as rhs:
            return is_equivalent(lhs.expr, rhs.expr)

        case UnaryExpr() as lhs, UnaryExpr() as rhs:
            return lhs.op == rhs.op and is_equivalent(lhs.expr, rhs.expr)

        case OpExpr() as lhs, OpExpr() as rhs:
            return (
                lhs.op == rhs.op
                and is_equivalent(lhs.left, rhs.left)
                and is_equivalent(lhs.right, rhs.right)
            )

        case ComparisonExpr() as lhs, ComparisonExpr() as rhs:
            return lhs.operators == rhs.operators and all(
                map(is_equivalent, lhs.operands, rhs.operands)
            )

        case SliceExpr() as lhs, SliceExpr() as rhs:
            return (
                is_equivalent(lhs.begin_index, rhs.begin_index)
                and is_equivalent(lhs.end_index, rhs.end_index)
                and is_equivalent(lhs.stride, rhs.stride)
            )

    return str(lhs) == str(rhs)


def get_common_expr_positions(*exprs: Expression) -> tuple[int, int] | None:
    for lhs, rhs in combinations(exprs, 2):
        if is_equivalent(lhs, rhs):
            return exprs.index(lhs), exprs.index(rhs)

    return None


def get_common_expr_in_comparison_chain(
    node: OpExpr, oper: str, cmp_oper: str = "=="
) -> tuple[Expression, tuple[int, int]] | None:
    """
    This function finds the first expression shared between 2 comparison
    expressions in the binary operator `oper`.

    For example, an OpExpr that looks like the following:

    1 == 2 or 3 == 1

    Will return a tuple containing the first common expression (`IntExpr(1)` in
    this case), and the indices of the common expressions as they appear in the
    source (`0` and `3` in this case). The indices are to be used for display
    purposes by the caller.

    If the binary operator is not composed of 2 comparison operators, or if
    there are no common expressions, `None` is returned.
    """

    match extract_binary_oper(oper, node):
        case (
            ComparisonExpr(operators=[lhs_oper], operands=[a, b]),
            ComparisonExpr(operators=[rhs_oper], operands=[c, d]),
        ) if lhs_oper == rhs_oper == cmp_oper and (
            indices := get_common_expr_positions(a, b, c, d)
        ):
            return a, indices

    return None  # pragma: no cover


class ReadCountVisitor(TraverserVisitor):
    name: NameExpr
    read_count: int

    def __init__(self, name: NameExpr) -> None:
        self.name = name
        self.read_count = 0

    def visit_name_expr(self, node: NameExpr) -> None:
        if node.fullname == self.name.fullname:
            self.read_count += 1

    @property
    def was_read(self) -> int:
        return self.read_count > 0


def is_name_unused_in_contexts(name: NameExpr, contexts: list[Node]) -> bool:
    for ctx in contexts:
        visitor = ReadCountVisitor(name)
        visitor.accept(ctx)

        if visitor.was_read:
            return False

    return True


def normalize_os_path(module: str | None) -> str:
    """
    Mypy turns "os.path" module names into their respective platform, such
    as "ntpath" for windows, "posixpath" if they are POSIX only, or
    "genericpath" if they apply to both (I assume). To make life easier
    for us though, we turn those module names into their original form.
    """

    # Used for compatibility with older versions of Mypy.
    if not module:
        return ""

    segments = module.split(".")

    if segments[0].startswith(("genericpath", "ntpath", "posixpath")):
        return ".".join(["os", "path"] + segments[1:])  # noqa: RUF005

    return module


def is_type_none_call(node: Expression) -> bool:
    match node:
        case CallExpr(
            callee=NameExpr(fullname="builtins.type"),
            args=[arg],
        ) if is_none_literal(arg):
            return True

    return False


def is_none_literal(node: Node) -> TypeGuard[NameExpr]:
    return isinstance(node, NameExpr) and node.fullname == "builtins.None"


def get_fstring_parts(expr: Expression) -> list[tuple[bool, Expression, str]]:
    match expr:
        case CallExpr(
            callee=MemberExpr(
                expr=StrExpr(value="{:{}}"),
                name="format",
            ),
            args=[arg, StrExpr(value=format_arg)],
            arg_kinds=[ArgKind.ARG_POS, ArgKind.ARG_POS],
        ):
            return [(True, arg, format_arg)]

        case CallExpr(
            callee=MemberExpr(
                expr=StrExpr(value=""),
                name="join",
            ),
            args=[ListExpr(items=items)],
            arg_kinds=[ArgKind.ARG_POS],
        ):
            exprs: list[tuple[bool, Expression, str]] = []

            had_at_least_one_fstring_part = False

            for item in items:
                if isinstance(item, StrExpr):
                    exprs.append((False, item, ""))

                elif tmp := get_fstring_parts(item):
                    had_at_least_one_fstring_part = True
                    exprs.extend(tmp)

                else:
                    return []

            if not had_at_least_one_fstring_part:
                return []

            return exprs

    return []


def stringify(node: Node) -> str:
    try:
        return _stringify(node)

    except ValueError:  # pragma: no cover
        return "x"


def _stringify(node: Node) -> str:
    match node:
        case MemberExpr(expr=expr, name=name):
            return f"{_stringify(expr)}.{name}"

        case NameExpr(name=name):
            return unmangle_name(name)

        case BytesExpr(value=value):
            # TODO: use same formatting as source line
            value = value.replace('"', r"\"")

            return f'b"{value}"'

        case IntExpr(value=value):
            # TODO: use same formatting as source line
            return str(value)

        case ComplexExpr(value=value):
            # TODO: use same formatting as source line
            return str(value)

        case FloatExpr(value=value):
            return str(value)

        case StrExpr(value=value):
            value = repr(value)[1:-1].replace('"', r"\"")

            return f'"{value}"'

        case DictExpr(items=items):
            parts: list[str] = []

            for k, v in items:
                if k:
                    parts.append(f"{stringify(k)}: {stringify(v)}")

                else:
                    parts.append(f"**{stringify(v)}")

            return f"{{{', '.join(parts)}}}"

        case TupleExpr(items=items):
            inner = ", ".join(stringify(x) for x in items)

            if len(items) == 1:
                # single element tuples need a trailing comma
                inner += ","

            return f"({inner})"

        case CallExpr(arg_names=arg_names, arg_kinds=arg_kinds, args=args):
            if fstring_parts := get_fstring_parts(node):
                output = 'f"'

                for is_format_arg, arg, fmt in fstring_parts:
                    if not is_format_arg:
                        assert isinstance(arg, StrExpr)

                        output += _stringify(arg)[1:-1]

                    elif fmt:
                        output += f"{{{_stringify(arg)}:{fmt}}}"

                    else:
                        output += f"{{{_stringify(arg)}}}"

                output += '"'
                return output

            call_args: list[str] = []

            for arg_name, kind, arg in zip(arg_names, arg_kinds, args):
                if kind == ArgKind.ARG_NAMED:
                    call_args.append(f"{arg_name}={_stringify(arg)}")

                elif kind == ArgKind.ARG_STAR:
                    call_args.append(f"*{_stringify(arg)}")

                elif kind == ArgKind.ARG_STAR2:
                    call_args.append(f"**{_stringify(arg)}")

                else:
                    call_args.append(_stringify(arg))

            return f"{_stringify(node.callee)}({', '.join(call_args)})"

        case IndexExpr(base=base, index=index):
            return f"{stringify(base)}[{stringify(index)}]"

        case SliceExpr(begin_index=begin_index, end_index=end_index, stride=stride):
            begin = stringify(begin_index) if begin_index else ""
            end = stringify(end_index) if end_index else ""
            stride = f":{stringify(stride)}" if stride else ""  # type: ignore[assignment]

            return f"{begin}:{end}{stride}"

        case OpExpr(left=left, op=op, right=right):
            return f"{_stringify(left)} {op} {_stringify(right)}"

        case ComparisonExpr():
            parts = []

            for op, operand in zip(node.operators, node.operands):
                parts.extend((_stringify(operand), op))

            parts.append(_stringify(node.operands[-1]))

            return " ".join(parts)

        case UnaryExpr(op=op, expr=expr):
            if op not in "+-~":
                op += " "

            return f"{op}{_stringify(expr)}"

        case LambdaExpr(
            arg_names=arg_names,
            arg_kinds=arg_kinds,
            body=Block(body=[ReturnStmt(expr=Expression() as expr)]),
        ) if all(kind == ArgKind.ARG_POS for kind in arg_kinds) and all(arg_names):
            if arg_names:
                args = " "  # type: ignore
                args += ", ".join(arg_names)  # type: ignore
            else:
                args = ""  # type: ignore

            body = _stringify(expr)

            return f"lambda{args}: {body}"

        case ListExpr(items=items):
            inner = ", ".join(stringify(x) for x in items)

            return f"[{inner}]"

        case SetExpr(items=items):
            inner = ", ".join(stringify(x) for x in items)

            return f"{{{inner}}}"

        # TODO: support multiple lvalues
        case AssignmentStmt(lvalues=[lhs], rvalue=rhs):
            return f"{stringify(lhs)} = {stringify(rhs)}"

        case IfStmt(expr=[expr], body=[Block(body=[stmt])], else_body=None):
            return f"if {_stringify(expr)}: {_stringify(stmt)}"

        case ForStmt(
            index=index,
            expr=expr,
            body=Block(body=[stmt]),
            else_body=None,
            is_async=False,
        ):
            return f"for {_stringify(index)} in {_stringify(expr)}: {_stringify(stmt)}"

        case ConditionalExpr(if_expr=if_true, cond=cond, else_expr=if_false):
            return f"{_stringify(if_true)} if {_stringify(cond)} else {_stringify(if_false)}"

        case DelStmt(expr=expr):
            return f"del {_stringify(expr)}"

        case ExpressionStmt(expr=expr):
            return _stringify(expr)

        case AwaitExpr(expr=expr):
            return f"await {_stringify(expr)}"

        case AssignmentExpr(target=lhs, value=rhs):
            return f"{_stringify(lhs)} := {_stringify(rhs)}"

    raise ValueError


def slice_expr_to_slice_call(expr: SliceExpr) -> str:
    args = [
        stringify(expr.begin_index) if expr.begin_index else "None",
        stringify(expr.end_index) if expr.end_index else "None",
    ]

    if expr.stride:
        args.append(stringify(expr.stride))

    return f"slice({', '.join(args)})"


TypeLike = type | str | object | None


def is_same_type(ty: Type | SymbolNode | None, *expected: TypeLike) -> bool:
    """
    Check if the type `ty` matches any of the `expected` types. `ty` must be a Mypy type object,
    but the expected types can be any of the following:

    * Built in type like `str`, `bool`, etc.
    * Fully-qualified type name (ie, `pathlib.Path`) as a `str`
    * `None`
    * `typing.Any`

    When `typing.Any` is used it will not match all types, instead it will only matches explicit
    `Any` types.
    """

    return any(_is_same_type(ty, t) for t in expected)


SIMPLE_TYPES: dict[str, type | object | None] = {
    "Any": Any,
    "None": None,
    "builtins.bool": bool,
    "builtins.bytearray": bytearray,
    "builtins.bytes": bytes,
    "builtins.complex": complex,
    "builtins.dict": dict,
    "builtins.float": float,
    "builtins.frozenset": frozenset,
    "builtins.int": int,
    "builtins.list": list,
    "builtins.set": set,
    "builtins.str": str,
    "builtins.tuple": tuple,
}


def _is_same_type(ty: Type | SymbolNode | None, expected: TypeLike) -> bool:
    if ty is expected is None:
        return True

    if isinstance(ty, TypeAliasType):
        if not ty.alias:
            return False  # pragma: no cover

        return _is_same_type(ty.alias.target, expected)

    if isinstance(ty, TupleType) and expected is tuple:
        return True

    if isinstance(ty, AnyType) and expected is Any:
        return True

    if isinstance(ty, Instance | TypeInfo):
        str_type = ty.type.fullname if isinstance(ty, Instance) else ty.fullname

        if str_type in SIMPLE_TYPES and SIMPLE_TYPES[str_type] is expected:
            return True

        if isinstance(expected, str) and str_type == expected:
            return True

    return False


def _get_builtin_mypy_type(name: str) -> Instance | None:
    if (sym := types.BUILTINS_MYPY_FILE.names.get(name)) and isinstance(sym.node, TypeInfo):
        return Instance(sym.node, [])

    return None  # pragma: no cover


def get_mypy_type(node: Node) -> Type | SymbolNode | None:
    # forward declaration to make Mypy happy
    ty: Type | SymbolNode | None

    match node:
        case StrExpr():
            return _get_builtin_mypy_type("str")

        case BytesExpr():
            return _get_builtin_mypy_type("bytes")

        case IntExpr():
            return _get_builtin_mypy_type("int")

        case FloatExpr():
            return _get_builtin_mypy_type("float")

        case ComplexExpr():
            return _get_builtin_mypy_type("complex")

        case NameExpr():
            if is_bool_literal(node):
                return _get_builtin_mypy_type("bool")

            if node.node:
                return get_mypy_type(node.node)

        case DictExpr():
            return _get_builtin_mypy_type("dict")

        case ListExpr():
            return _get_builtin_mypy_type("list")

        case TupleExpr():
            return _get_builtin_mypy_type("tuple")

        case SetExpr():
            return _get_builtin_mypy_type("set")

        case Var(type=ty) | FuncDef(type=ty):
            return ty

        case TypeInfo() | TypeAlias() | MypyFile():
            return node

        case MemberExpr(expr=lhs, name=name):
            ty = get_mypy_type(lhs)

            if (
                isinstance(ty, MypyFile | TypeInfo)
                and (member := ty.names.get(name))
                and member.node
            ):
                return get_mypy_type(member.node)

            if isinstance(ty, Instance) and (member := ty.type.get(name)) and member.node:
                return get_mypy_type(member.node)

        case CallExpr(analyzed=CastExpr(type=ty)):
            return ty

        case CallExpr(callee=callee):
            match get_mypy_type(callee):
                case CallableType(ret_type=ty):
                    return ty

                case TypeAlias(target=ty):
                    return ty  # pragma: no cover

                case TypeInfo() as sym:
                    return Instance(sym, [])

        case UnaryExpr(op="not"):
            return _get_builtin_mypy_type("bool")

        case UnaryExpr(method_type=CallableType(ret_type=ty)):
            return ty

        case OpExpr(method_type=CallableType(ret_type=ty)):
            return ty

        case IndexExpr(method_type=CallableType(ret_type=ty)):
            return ty

        case AwaitExpr(expr=expr):
            ty = get_mypy_type(expr)

            # TODO: allow for any Awaitable[T] type
            match ty:
                case Instance(type=TypeInfo(fullname="typing.Coroutine"), args=[_, _, rtype]):
                    return rtype

                case Instance(
                    type=TypeInfo(fullname="asyncio.tasks.Task" | "_asyncio.Task"),
                    args=[rtype],
                ):
                    return rtype

        case LambdaExpr(body=Block(body=[ReturnStmt(expr=expr)])) if expr:
            if (ty := get_mypy_type(expr)) and isinstance(ty, Type):
                return _build_placeholder_callable(ty)

        case AssignmentExpr(target=expr):
            return get_mypy_type(expr)

    return None


def _build_placeholder_callable(rtype: Type) -> Type | None:
    if function := _get_builtin_mypy_type("function"):
        return CallableType([], [], [], ret_type=rtype, fallback=function)

    return None  # pragma: no cover


def mypy_type_to_python_type(ty: Type | SymbolNode | None) -> type | None:
    match ty:
        # TODO: return annotated types if instance has args (ie, `list[int]`)
        case Instance(type=TypeInfo(fullname=fullname)):
            return SIMPLE_TYPES.get(fullname)  # type: ignore

    return None  # pragma: no cover


def is_mapping(expr: Expression) -> bool:
    return is_mapping_type(get_mypy_type(expr))


def is_mapping_type(ty: Type | SymbolNode | None) -> bool:
    return is_subclass(ty, "typing.Mapping")


def is_bool_literal(node: Node) -> TypeGuard[NameExpr]:
    return is_true_literal(node) or is_false_literal(node)


def is_true_literal(node: Node) -> TypeGuard[NameExpr]:
    return isinstance(node, NameExpr) and node.fullname == "builtins.True"


def is_false_literal(node: Node) -> TypeGuard[NameExpr]:
    return isinstance(node, NameExpr) and node.fullname == "builtins.False"


def is_sized(node: Expression) -> bool:
    return is_sized_type(get_mypy_type(node))


def is_sized_type(ty: Type | SymbolNode | None) -> bool:
    # Certain object MROs (like dict) doesn't reference Sized directly, only Collection. We might
    # need to add more derived Sized types if Mypy doesn't fully resolve the MRO.

    return is_subclass(ty, "typing.Sized", "typing.Collection")


def is_subclass(ty: Any, *expected: TypeLike) -> bool:  # type: ignore[explicit-any]
    if type_info := extract_typeinfo(ty):
        return any(is_same_type(x, *expected) for x in type_info.mro)

    return False  # pragma: no cover


def extract_typeinfo(ty: Type | SymbolNode | None) -> TypeInfo | None:
    match ty:
        case TypeInfo():
            return ty  # pragma: no cover

        case Instance():
            return ty.type

        case TupleType():
            tmp = _get_builtin_mypy_type("tuple")
            assert tmp

            return tmp.type

    return None  # pragma: no cover
