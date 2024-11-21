from dataclasses import dataclass

from mypy.nodes import (
    ArgKind,
    Block,
    ComparisonExpr,
    FuncItem,
    IndexExpr,
    LambdaExpr,
    NameExpr,
    OpExpr,
    ReturnStmt,
    SliceExpr,
    TupleExpr,
    UnaryExpr,
)

from refurb.checks.common import (
    _stringify,
    get_mypy_type,
    is_same_type,
    slice_expr_to_slice_call,
    stringify,
)
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Don't write lambdas/functions to wrap builtin operators, use the `operator`
    module instead:

    Bad:

    ```
    from functools import reduce

    nums = [1, 2, 3]

    print(reduce(lambda x, y: x + y, nums))  # 6
    ```

    Good:

    ```
    from functools import reduce
    from operator import add

    nums = [1, 2, 3]

    print(reduce(add, nums))  # 6
    ```

    In addition, the `operator.itemgetter()` function can be used to get one or
    more items from an object, removing the need to create a lambda just to
    extract values from an object:

    Bad:

    ```
    row = (1, "Some text", True)

    transform = lambda x: (x[2], x[0])
    ```

    Good:

    ```
    from operator import itemgetter

    row = (1, "Some text", True)

    transform = itemgetter(2, 0)
    ```
    """

    name = "use-operator"
    code = 118
    categories = ("operator",)


BINARY_OPERATORS = {
    "+": "add",
    "in": "contains",
    "/": "truediv",
    "//": "floordiv",
    "&": "and_",
    "^": "xor",
    "|": "or_",
    "**": "pow",
    "is": "is_",
    "is not": "is_not",
    "<<": "lshift",
    "%": "mod",
    "*": "mul",
    "@": "matmul",
    ">>": "rshift",
    "-": "sub",
    "<": "lt",
    "<=": "le",
    "==": "eq",
    "!=": "ne",
    ">=": "ge",
    ">": "gt",
}

UNARY_OPERATORS = {
    "~": "invert",
    "-": "neg",
    "not": "not_",
    "+": "pos",
}


def check(node: FuncItem, errors: list[Error]) -> None:
    func_type = get_function_type(node)

    match node:
        case FuncItem(
            arg_names=[lhs_name, rhs_name],
            arg_kinds=[ArgKind.ARG_POS, ArgKind.ARG_POS],
            body=Block(
                body=[
                    ReturnStmt(
                        expr=OpExpr(
                            op=op,
                            left=NameExpr(name=expr_lhs),
                            right=NameExpr(name=expr_rhs),
                        )
                        | ComparisonExpr(
                            operators=[op],
                            operands=[
                                NameExpr(name=expr_lhs),
                                NameExpr(name=expr_rhs),
                            ],
                        ),
                    )
                ]
            ),
        ) if func_name := BINARY_OPERATORS.get(op):
            if func_name == "contains":
                # operator.contains has reversed parameters
                expr_lhs, expr_rhs = expr_rhs, expr_lhs

            if lhs_name == expr_lhs and rhs_name == expr_rhs:
                errors.append(
                    ErrorInfo.from_node(
                        node,
                        f"Replace {func_type} with `operator.{func_name}`",
                    )
                )

        case FuncItem(
            arg_names=[name],
            arg_kinds=[ArgKind.ARG_POS],
            body=Block(body=[ReturnStmt(expr=expr)]),
        ):
            match expr:
                case UnaryExpr(
                    op=op,
                    expr=NameExpr(name=expr_name),
                ) if name == expr_name and (func_name := UNARY_OPERATORS.get(op)):
                    errors.append(
                        ErrorInfo.from_node(
                            node,
                            f"Replace {func_type} with `operator.{func_name}`",
                        )
                    )

                case IndexExpr(base=NameExpr() as base, index=index) if base.name == name:
                    match index:
                        case SliceExpr(
                            begin_index=None,
                            end_index=None,
                            stride=None,
                        ) if is_same_type(get_mypy_type(base), list):
                            new = "list.copy"

                        case SliceExpr():
                            new = f"operator.itemgetter({slice_expr_to_slice_call(index)})"

                        case _:
                            new = f"operator.itemgetter({stringify(index)})"

                    msg = f"Replace {func_type} with `{new}`"

                    errors.append(ErrorInfo.from_node(node, msg))

                case TupleExpr(items=items) if len(items) > 1:
                    tuple_args: list[str] = []

                    for item in items:
                        match item:
                            case IndexExpr(
                                base=NameExpr(name=item_name),
                                index=index,
                            ) if item_name == name:
                                tuple_args.append(
                                    slice_expr_to_slice_call(index)
                                    if isinstance(index, SliceExpr)
                                    else stringify(index)
                                )

                            case _:
                                return

                    inner = ", ".join(tuple_args)

                    msg = f"Replace {func_type} with `operator.itemgetter({inner})`"

                    errors.append(ErrorInfo.from_node(node, msg))


def get_function_type(node: FuncItem) -> str:
    if isinstance(node, LambdaExpr):
        try:
            return f"`{_stringify(node)}`"

        except ValueError:
            return "lambda"

    return "function"
