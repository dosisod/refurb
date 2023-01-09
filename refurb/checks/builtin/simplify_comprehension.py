from dataclasses import dataclass

from mypy.nodes import (
    CallExpr,
    GeneratorExpr,
    ListComprehension,
    NameExpr,
    SetComprehension,
)

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Often times generator and comprehension expressions can be written more
    succinctly. For example, passing a list comprehension to a function when
    a generator expression would suffice, or using the shorthand notation
    in the case of `list` and `set`. For example:

    Bad:

    ```
    nums = [1, 1, 2, 3]

    nums_times_10 = list(num * 10 for num in nums)
    unique_squares = set(num ** 2 for num in nums)
    number_tuple = tuple([num ** 2 for num in nums])
    ```

    Good:

    ```
    nums = [1, 1, 2, 3]

    nums_times_10 = [num * 10 for num in nums]
    unique_squares = {num ** 2 for num in nums}
    number_tuple = tuple(num ** 2 for num in nums)
    ```
    """

    name = "simplify-comprehension"
    enabled = False
    code = 137
    categories = ["builtin", "iterable", "readability"]


FUNCTION_MAPPINGS = {
    "builtins.list": "[...]",
    "builtins.set": "{...}",
    "builtins.frozenset": "frozenset(...)",
    "builtins.tuple": "tuple(...)",
}

SET_TYPES = ("frozenset", "set")
COMPREHENSION_SHORTHAND_TYPES = ("list", "set")

NODE_TYPE_TO_FUNC_NAME = {
    ListComprehension: "builtins.list",
    SetComprehension: "builtins.set",
    GeneratorExpr: "",
}


def format_func_name(fullname: str) -> str:
    return FUNCTION_MAPPINGS.get(fullname, "...")


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=NameExpr(name=name, fullname=fullname),
            args=[
                GeneratorExpr()
                | ListComprehension()
                | SetComprehension() as arg
            ],
        ) if fullname in FUNCTION_MAPPINGS:
            if (
                isinstance(arg, GeneratorExpr)
                and name not in COMPREHENSION_SHORTHAND_TYPES
            ):
                return

            if isinstance(arg, SetComprehension) and name not in SET_TYPES:
                return

            old = format_func_name(NODE_TYPE_TO_FUNC_NAME[type(arg)])
            new = format_func_name(fullname)

            errors.append(
                ErrorInfo(
                    node.line,
                    node.column,
                    f"Replace `{name}({old})` with `{new}`",
                )
            )
