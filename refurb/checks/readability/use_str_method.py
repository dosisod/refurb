from dataclasses import dataclass
from typing import Any

from mypy.nodes import ArgKind, Block, CallExpr, LambdaExpr, MemberExpr, NameExpr, ReturnStmt

from refurb.checks.common import get_mypy_type, is_same_type, stringify
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Don't use a lambda function to call a no-arg method on a string, use the
    name of the string method directly. It is faster, and often times improves
    readability.

    Bad:

    ```
    def normalize_phone_number(phone_number: str) -> int:
        digits = filter(lambda x: x.isdigit(), phone_number)

        return int("".join(digits))
    ```

    Good:

    ```
    def normalize_phone_number(phone_number: str) -> int:
        digits = filter(str.isdigit, phone_number)

        return int("".join(digits))
    ```
    """

    name = "use-str-method"
    categories = ("performance", "readability")
    code = 190


STR_FUNCS = frozenset(
    (
        "capitalize",
        "casefold",
        "isalnum",
        "isalpha",
        "isascii",
        "isdecimal",
        "isdigit",
        "isidentifier",
        "islower",
        "isnumeric",
        "isprintable",
        "isspace",
        "istitle",
        "isupper",
        "lower",
        "lstrip",
        "rsplit",
        "rstrip",
        "split",
        "splitlines",
        "strip",
        "swapcase",
        "title",
        "upper",
    )
)


def check(node: LambdaExpr, errors: list[Error]) -> None:
    match node:
        case LambdaExpr(
            arg_names=[arg_name],
            arg_kinds=[ArgKind.ARG_POS],
            body=Block(
                body=[
                    ReturnStmt(
                        expr=CallExpr(
                            callee=MemberExpr(
                                expr=NameExpr(name=member_base_name) as member_base,
                                name=str_func_name,
                            ),
                            args=[],
                        ),
                    )
                ]
            ),
        ) if (
            arg_name == member_base_name
            and str_func_name in STR_FUNCS
            and is_same_type(get_mypy_type(member_base), str, None, Any)
        ):
            msg = f"Replace `{stringify(node)}` with `str.{str_func_name}`"

            errors.append(ErrorInfo.from_node(node, msg))
