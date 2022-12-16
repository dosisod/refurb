from dataclasses import dataclass

from mypy.nodes import ComparisonExpr, Expression, NameExpr, Var

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Don't use `is` or `is not` to check if a boolean is True or False, simply
    use the name itself:

    Bad:

    ```
    failed = True

    if failed is True:
        print("You failed")
    ```

    Good:

    ```
    failed = True

    if failed:
        print("You failed")
    ```
    """

    code = 149


def is_bool_literal(expr: Expression) -> bool:
    match expr:
        case NameExpr(fullname="builtins.True" | "builtins.False"):
            return True

    return False


def is_bool_variable(expr: Expression) -> bool:
    match expr:
        case NameExpr(node=Var(type=ty)) if str(ty) == "builtins.bool":
            return True

    return False


IS_TRUTHY: dict[tuple[str, str], bool] = {
    ("is", "True"): True,
    ("is", "False"): False,
    ("is not", "True"): False,
    ("is not", "False"): True,
}


def check(node: ComparisonExpr, errors: list[Error]) -> None:
    match node:
        case ComparisonExpr(
            operators=["is" | "is not" as oper],
            operands=[NameExpr() as lhs, NameExpr() as rhs],
        ):
            if is_bool_literal(lhs) and is_bool_variable(rhs):
                old = f"{lhs.name} {oper} x"
                new = "x" if IS_TRUTHY[(oper, lhs.name)] else "not x"

            elif is_bool_variable(lhs) and is_bool_literal(rhs):
                old = f"x {oper} {rhs.name}"
                new = "x" if IS_TRUTHY[(oper, rhs.name)] else "not x"

            else:
                return

            errors.append(
                ErrorInfo(
                    node.line,
                    node.column,
                    f"Replace `{old}` with `{new}`",
                )
            )
