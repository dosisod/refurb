from dataclasses import dataclass

from mypy.nodes import CallExpr, MemberExpr, RefExpr

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    When constructing a Fraction or Decimal using a float, don't use the
    `from_float()` or `from_decimal()` class methods: Just use the more consice
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
    "Decimal.from_float",
    "Fraction.from_float",
    "Fraction.from_decimal",
}


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=MemberExpr(
                expr=RefExpr(
                    fullname="_decimal.Decimal" | "fractions.Fraction",
                    name=klass,  # type: ignore
                ),
                name="from_float" | "from_decimal" as ctor,
            ),
            args=[_],
        ):
            func = f"{klass}.{ctor}"

            if func not in KNOWN_FUNCS:
                return

            errors.append(
                ErrorInfo.from_node(
                    node, f"Replace `{func}(x)` with `{klass}(x)`"
                )
            )
