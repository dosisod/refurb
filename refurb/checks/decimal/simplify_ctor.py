from dataclasses import dataclass

from mypy.nodes import CallExpr, NameExpr, StrExpr

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
    categories = ["decimal"]


FLOAT_LITERALS = ["inf", "-inf", "infinity", "-infinity", "nan"]


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=NameExpr(fullname="_decimal.Decimal"),
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

                    msg = f'Replace `Decimal("{old}")` with `Decimal({new})`'

                    errors.append(ErrorInfo(node.line, node.column, msg))

                case CallExpr(
                    callee=NameExpr(fullname="builtins.float"),
                    args=[StrExpr(value=value)],
                ) if value.lower() in FLOAT_LITERALS:
                    msg = f'Replace `Decimal(float("{value}"))` with `Decimal("{value}")'  # noqa: E501

                    errors.append(ErrorInfo(node.line, node.column, msg))
