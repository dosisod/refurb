from dataclasses import dataclass

from mypy.nodes import (
    ArgKind,
    Block,
    ComparisonExpr,
    FuncItem,
    LambdaExpr,
    NameExpr,
    OpExpr,
    ReturnStmt,
    UnaryExpr,
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
    """

    name = "use-operator"
    code = 118
    categories = ["operator"]


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
    func_type = "lambda" if isinstance(node, LambdaExpr) else "function"

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
        ) if lhs_name == expr_lhs and rhs_name == expr_rhs:
            if func_name := BINARY_OPERATORS.get(op):
                errors.append(
                    ErrorInfo(
                        node.line,
                        node.column,
                        f"Replace {func_type} with `operator.{func_name}`",
                    )
                )

        case FuncItem(
            arg_names=[name],
            arg_kinds=[ArgKind.ARG_POS],
            body=Block(
                body=[
                    ReturnStmt(
                        expr=UnaryExpr(
                            op=op,
                            expr=NameExpr(name=expr_name),
                        )
                    )
                ]
            ),
        ) if name == expr_name:
            if func_name := UNARY_OPERATORS.get(op):
                errors.append(
                    ErrorInfo(
                        node.line,
                        node.column,
                        f"Replace {func_type} with `operator.{func_name}`",
                    )
                )
