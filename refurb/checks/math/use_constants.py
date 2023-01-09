from dataclasses import dataclass

from mypy.nodes import FloatExpr

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Don't hardcode math constants like pi, tau, or e, use the `math.pi`,
    `math.tau`, or `math.e` constants respectively.

    Bad:

    ```
    def area(r: float) -> float:
        return 3.1415 * r * r
    ```

    Good:

    ```
    import math

    def area(r: float) -> float:
        return math.pi * r * r
    ```
    """

    name = "use-math-constant"
    code = 152
    categories = ["math", "readability"]


CONSTANTS = {
    "pi": "3.14",
    "e": "2.71",
    "tau": "6.28",
}


def check(node: FloatExpr, errors: list[Error]) -> None:
    num = str(node.value)

    if len(num) <= 3:
        return None

    for name, value in CONSTANTS.items():
        if num.startswith(value):
            errors.append(
                ErrorInfo(
                    node.line,
                    node.column,
                    f"Replace `{num}` with `math.{name}`",
                )
            )
