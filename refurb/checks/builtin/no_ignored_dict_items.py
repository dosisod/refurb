from dataclasses import dataclass

from mypy.nodes import (
    CallExpr,
    DictionaryComprehension,
    ForStmt,
    GeneratorExpr,
    MemberExpr,
    NameExpr,
    Node,
    TupleExpr,
    Var,
)

from refurb.checks.common import (
    check_for_loop_like,
    is_name_unused_in_contexts,
    is_placeholder,
)
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Don't use `.items()` on a `dict` if you only care about the keys or the
    values, but not both:

    Bad:

    ```
    books = {"Frank Herbert": "Dune"}

    for author, _ in books.items():
        print(author)

    for _, book in books.items():
        print(book)
    ```

    Good:

    ```
    books = {"Frank Herbert": "Dune"}

    for author in books:
        print(author)

    for book in books.values():
        print(book)
    ```
    """

    name = "no-ignored-dict-items"
    code = 135
    categories = ["dict"]


def check(
    node: ForStmt | GeneratorExpr | DictionaryComprehension,
    errors: list[Error],
) -> None:
    check_for_loop_like(check_dict_items_call, node, errors)


def check_dict_items_call(
    index: Node, expr: Node, contexts: list[Node], errors: list[Error]
) -> None:
    match index, expr:
        case (
            TupleExpr(items=[NameExpr() as key, NameExpr() as value]),
            CallExpr(
                callee=MemberExpr(
                    expr=NameExpr(node=Var(type=ty)),
                    name="items",
                )
            ),
        ) if str(ty).startswith("builtins.dict["):
            check_unused_key_or_value(key, value, contexts, errors)


def check_unused_key_or_value(
    key: NameExpr, value: NameExpr, contexts: list[Node], errors: list[Error]
) -> None:
    if is_placeholder(key) or is_name_unused_in_contexts(key, contexts):
        errors.append(
            ErrorInfo(
                key.line,
                key.column,
                "Key is unused, use `for value in d.values()` instead",
            )
        )

    if is_placeholder(value) or is_name_unused_in_contexts(value, contexts):
        errors.append(
            ErrorInfo(
                value.line,
                value.column,
                "Value is unused, use `for key in d` instead",
            )
        )
