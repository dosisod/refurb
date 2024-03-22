from dataclasses import dataclass

from mypy.nodes import CallExpr, IndexExpr, IntExpr, NameExpr, UnaryExpr

from refurb.checks.common import is_true_literal, stringify
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Don't use `sorted()` to get the min/max value out of an iterable element,
    use `min()` or `max()`.

    Bad:

    ```
    nums = [3, 1, 4, 1, 5]

    lowest = sorted(nums)[0]
    highest = sorted(nums)[-1]
    ```

    Good:

    ```
    nums = [3, 1, 4, 1, 5]

    lowest = min(nums)
    highest = max(nums)
    ```
    """

    name = "no-sorted-min-max"
    code = 192
    categories = ("builtin", "performance", "readability")


def check(node: IndexExpr, errors: list[Error]) -> None:
    match node:
        case IndexExpr(
            base=CallExpr(
                callee=NameExpr(fullname="builtins.sorted"),
                args=[arg1, *args],
                arg_names=[_, *arg_names],
            ),
            index=IntExpr(value=0) | UnaryExpr(op="-", expr=IntExpr(value=1)) as index,
        ):
            is_zero_index = isinstance(index, IntExpr)
            is_reversed = False
            key = ""

            for arg_name, arg in zip(arg_names, args):
                if arg_name == "reverse":
                    if not is_true_literal(arg):
                        return

                    is_reversed = True

                elif arg_name == "key":
                    key = f", key={stringify(arg)}"

                else:
                    return

            func = "max" if is_zero_index == is_reversed else "min"

            old = stringify(node)
            new = f"{func}({stringify(arg1)}{key})"
            msg = f"Replace `{old}` with `{new}`"

            errors.append(ErrorInfo.from_node(node, msg))
