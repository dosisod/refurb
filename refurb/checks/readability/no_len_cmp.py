from dataclasses import dataclass

from mypy.nodes import (
    CallExpr,
    ComparisonExpr,
    DictExpr,
    Expression,
    IntExpr,
    ListExpr,
    NameExpr,
    StrExpr,
    TupleExpr,
    Var,
)

from refurb.error import Error


@dataclass
class ErrorNoLenCompare(Error):
    """
    Don't check a container's length to determine if it is empty or not, use
    a truthiness check instead:

    Bad:

    ```
    name = "bob"
    if len(name) == 0:
        pass

    nums = [1, 2, 3]
    if len(nums) >= 1:
        pass
    ```

    Good:

    ```
    name = "bob"
    if not name:
        pass

    nums = [1, 2, 3]
    if nums:
        pass
    ```
    """

    code = 115


CONTAINER_TYPES = {
    "builtins.list",
    "builtins.tuple",
    "builtins.dict",
    "builtins.set",
    "builtins.frozenset",
    "builtins.str",
    "Tuple",
}


def is_builtin_container_type(type: str) -> bool:
    return any(type.startswith(x) for x in CONTAINER_TYPES)


def is_builtin_container_like(node: Expression) -> bool:
    match node:
        case NameExpr(node=Var(type=ty)) if is_builtin_container_type(str(ty)):
            return True

        case CallExpr(
            callee=NameExpr(fullname=name)
        ) if is_builtin_container_type(name or ""):
            return True

        case DictExpr() | ListExpr() | StrExpr() | TupleExpr():
            return True

    return False


IS_COMPARISON_TRUTHY: dict[tuple[str, int], bool] = {
    ("==", 0): False,
    ("<=", 0): False,
    (">", 0): True,
    ("!=", 0): True,
    (">=", 1): True,
}


def check(node: ComparisonExpr, errors: list[Error]) -> None:
    match node:
        case ComparisonExpr(
            operators=[oper],
            operands=[
                CallExpr(
                    callee=NameExpr(fullname="builtins.len"),
                    args=[arg],
                ),
                IntExpr(value=num),
            ],
        ) if is_builtin_container_like(arg):
            is_truthy = IS_COMPARISON_TRUTHY.get((oper, num))

            if is_truthy is None:
                return

            expr = "x" if is_truthy else "not x"

            errors.append(
                ErrorNoLenCompare(
                    node.line,
                    node.column,
                    f"Use `{expr}` instead of `len(x) {oper} {num}`",
                )
            )
