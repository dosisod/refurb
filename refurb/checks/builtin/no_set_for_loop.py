from dataclasses import dataclass

from mypy.nodes import (
    Block,
    CallExpr,
    ExpressionStmt,
    ForStmt,
    MemberExpr,
    NameExpr,
    Var,
)

from refurb.checks.common import unmangle_name
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    When you want to add/remove a bunch of items to/from a set, don't use a for
    loop, call the appropriate method on the set itself.

    Bad:

    ```
    sentence = "hello world"
    vowels = "aeiou"
    letters = set(sentence)

    for vowel in vowels:
        letters.discard(vowel)
    ```

    Good:

    ```
    sentence = "hello world"
    vowels = "aeiou"
    letters = set(sentence)

    letters.difference_update(vowels)
    ```
    """

    name = "no-set-for-loop"
    code = 142
    categories = ["builtin"]


def check(node: ForStmt, errors: list[Error]) -> None:
    match node:
        case ForStmt(
            index=NameExpr(name=for_name),
            body=Block(
                body=[
                    ExpressionStmt(
                        expr=CallExpr(
                            callee=MemberExpr(
                                expr=NameExpr(node=Var(type=ty)) as set_name,
                                name=("add" | "discard") as name,
                            ),
                            args=[arg],
                        )
                    )
                ]
            ),
        ) if str(ty).startswith("builtins.set[") and set_name.name != for_name:
            new_func = "update" if name == "add" else "difference_update"

            if isinstance(arg, NameExpr):
                expr = unmangle_name(arg.name)
                new_expr = "y"

                if unmangle_name(for_name) != expr:
                    return

            else:
                expr = "..."
                new_expr = "... for x in y"

            errors.append(
                ErrorInfo(
                    node.line,
                    node.column,
                    f"Replace `for x in y: s.{name}({expr})` with `s.{new_func}({new_expr})`",  # noqa: E501
                )
            )
