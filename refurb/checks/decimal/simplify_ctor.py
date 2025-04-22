from dataclasses import dataclass

from mypy.nodes import CallExpr, MemberExpr, NameExpr, RefExpr, StrExpr

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Under certain circumstances the `Decimal()` constructor can be made more
    succinct.

    Bad:

    ```
    if x == Decimal("0"):
        pass

    if y == Decimal(float("Infinity")):
        pass
    ```

    Good:

    ```
    if x == Decimal(0):
        pass

    if y == Decimal("Infinity"):
        pass
    ```
    """

    name = "simplify-decimal-ctor"
    code = 157
    categories = ("decimal",)


FLOAT_LITERALS = ["inf", "-inf", "infinity", "-infinity", "nan"]


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=RefExpr(fullname="decimal.Decimal" | "_decimal.Decimal") as ref,
            args=[arg],
        ):
            match arg:
                case StrExpr(value=value):
                    old = repr(value)[1:-1]

                    try:
                        new = value.strip().lstrip("+")

                        if int(value) != 0:
                            new = new.lstrip("0")

                    except ValueError:
                        return

                    func_name = stringify_decimal_expr(ref)

                    msg = f'Replace `{func_name}("{old}")` with `{func_name}({new})`'  # noqa: E501

                    errors.append(ErrorInfo.from_node(node, msg))

                case CallExpr(
                    callee=NameExpr(fullname="builtins.float"),
                    args=[StrExpr(value=value)],
                ) if value.lower() in FLOAT_LITERALS:
                    func_name = stringify_decimal_expr(ref)

                    msg = f'Replace `{func_name}(float("{value}"))` with `{func_name}("{value}")`'  # noqa: E501

                    errors.append(ErrorInfo.from_node(node, msg))


def stringify_decimal_expr(node: RefExpr) -> str:
    return "decimal.Decimal" if isinstance(node, MemberExpr) else "Decimal"
