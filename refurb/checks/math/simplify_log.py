from dataclasses import dataclass

from mypy.nodes import CallExpr, FloatExpr, IntExpr, RefExpr

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Use the shorthand `log2` and `log10` functions instead of passing 2 or 10
    as the second argument to the `log` function. If `math.e` is used as the
    second argument, just use `math.log(x)` instead, since `e` is the default.

    Bad:

    ```
    power = math.log(x, 10)
    ```

    Good:

    ```
    power = math.log10(x)
    ```
    """

    name = "simplify-math-log"
    code = 163
    categories = ("math", "readability")


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=RefExpr(fullname="math.log"),
            args=[_, arg],
        ):
            match arg:
                case IntExpr(value=2 | 10) | FloatExpr(value=2.0 | 10.0):
                    base = str(arg.value)
                    new = f"math.log{int(arg.value)}(x)"

                case RefExpr(fullname="math.e"):
                    base = "math.e"
                    new = "math.log(x)"

                case _:
                    return

            errors.append(
                ErrorInfo.from_node(
                    node, f"Replace `math.log(x, {base})` with `{new}`"
                )
            )
