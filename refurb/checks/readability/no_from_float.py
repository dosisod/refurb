from dataclasses import dataclass

from mypy.nodes import CallExpr, MemberExpr, RefExpr

from refurb.checks.common import stringify
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    When constructing a Fraction or Decimal using a float, don't use the
    `from_float()` or `from_decimal()` class methods: Just use the more concise
    `Fraction()` and `Decimal()` class constructors instead.

    Bad:

    ```
    ratio = Fraction.from_float(1.2)
    score = Decimal.from_float(98.0)
    ```

    Good:

    ```
    ratio = Fraction(1.2)
    score = Decimal(98.0)
    ```
    """

    name = "no-from-float"
    code = 164
    categories = ("decimal", "fractions", "readability")


KNOWN_FUNCS = {
    "_decimal.Decimal.from_float",
    "decimal.Decimal.from_float",
    "fractions.Fraction.from_float",
    "fractions.Fraction.from_decimal",
}


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=MemberExpr(
                expr=RefExpr(
                    fullname="decimal.Decimal" | "_decimal.Decimal" | "fractions.Fraction"
                ) as ref,
                name="from_float" | "from_decimal" as ctor,
            ),
            args=[arg],
        ):
            if f"{ref.fullname}.{ctor}" not in KNOWN_FUNCS:
                return

            base = stringify(ref)
            arg = stringify(arg)  # type: ignore

            old = f"{base}.{ctor}({arg})"
            new = f"{base}({arg})"

            errors.append(ErrorInfo.from_node(node, f"Replace `{old}` with `{new}`"))
