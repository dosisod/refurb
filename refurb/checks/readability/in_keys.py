from dataclasses import dataclass

from mypy.nodes import CallExpr, ComparisonExpr, MemberExpr

from refurb.checks.common import is_mapping, stringify
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    If you only want to check if a key exists in a dictionary, you don't need
    to call `.keys()` first, just use `in` on the dictionary itself:

    Bad:

    ```
    d = {"key": "value"}

    if "key" in d.keys():
        ...
    ```

    Good:

    ```
    d = {"key": "value"}

    if "key" in d:
        ...
    ```
    """

    name = "no-in-dict-keys"
    code = 130
    categories = ("dict", "readability")


def check(node: ComparisonExpr, errors: list[Error]) -> None:
    match node:
        case ComparisonExpr(
            operators=["in" | "not in" as oper],
            operands=[
                _,
                CallExpr(
                    callee=MemberExpr(expr=dict_expr, name="keys"),
                    args=[],
                ) as expr,
            ],
        ) if is_mapping(dict_expr):
            dict_expr = stringify(dict_expr)  # type: ignore

            msg = f"Replace `{oper} {stringify(expr)}` with `{oper} {dict_expr}`"

            errors.append(ErrorInfo.from_node(expr, msg))
