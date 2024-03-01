from dataclasses import dataclass

from mypy.nodes import (
    CallExpr,
    DictionaryComprehension,
    Expression,
    ForStmt,
    GeneratorExpr,
    MemberExpr,
    NameExpr,
    Node,
    TupleExpr,
)

from refurb.checks.common import (
    check_for_loop_like,
    is_mapping,
    is_name_unused_in_contexts,
    stringify,
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
    categories = ("dict",)


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
                callee=MemberExpr(expr=dict_expr, name="items"),
                args=[],
            ),
        ) if is_mapping(dict_expr):
            check_unused_key_or_value(key, value, contexts, errors, dict_expr)


def check_unused_key_or_value(
    key: NameExpr,
    value: NameExpr,
    contexts: list[Node],
    errors: list[Error],
    dict_expr: Expression,
) -> None:
    if is_name_unused_in_contexts(key, contexts):
        msg = f"Key is unused, use `for {stringify(value)} in {stringify(dict_expr)}.values()` instead"  # noqa: E501

        errors.append(ErrorInfo.from_node(key, msg))

    if is_name_unused_in_contexts(value, contexts):
        msg = f"Value is unused, use `for {stringify(key)} in {stringify(dict_expr)}` instead"

        errors.append(ErrorInfo.from_node(value, msg))
