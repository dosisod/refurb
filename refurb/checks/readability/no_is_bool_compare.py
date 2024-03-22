from dataclasses import dataclass

from mypy.nodes import ComparisonExpr, Expression

from refurb.checks.common import get_mypy_type, is_bool_literal, is_same_type, stringify
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Don't use `is` or `==` to check if a boolean is True or False, simply
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

    name = "no-bool-literal-compare"
    code = 149
    categories = ("logical", "readability", "truthy")


def is_bool_variable(expr: Expression) -> bool:
    return is_same_type(get_mypy_type(expr), bool)


def is_truthy(oper: str, name: str) -> bool:
    value = name == "True"

    return not value if oper in {"is not", "!="} else value


def check(node: ComparisonExpr, errors: list[Error]) -> None:
    match node:
        case ComparisonExpr(
            operators=["is" | "is not" | "==" | "!=" as oper],
            operands=[lhs, rhs],
        ):
            if is_bool_literal(lhs) and is_bool_variable(rhs):
                expr = stringify(rhs)

                old = f"{lhs.name} {oper} {expr}"
                new = expr if is_truthy(oper, lhs.name) else f"not {expr}"

            elif is_bool_variable(lhs) and is_bool_literal(rhs):
                expr = stringify(lhs)

                old = f"{expr} {oper} {rhs.name}"
                new = expr if is_truthy(oper, rhs.name) else f"not {expr}"

            else:
                return

            errors.append(ErrorInfo.from_node(node, f"Replace `{old}` with `{new}`"))
