from dataclasses import dataclass

from mypy.nodes import (
    CallExpr,
    DictionaryComprehension,
    ForStmt,
    GeneratorExpr,
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
    Don't use `enumerate` if you are disregarding either the index or the
    value:

    Bad:

    ```
    books = ["Ender's Game", "The Black Swan"]

    for index, _ in enumerate(books):
        print(index)

    for _, book in enumerate(books):
        print(book)
    ```

    Good:

    ```
    books = ["Ender's Game", "The Black Swan"]

    for index in range(len(books)):
        print(index)

    for book in books:
        print(book)
    ```
    """

    name = "no-ignored-enumerate-items"
    code = 148
    categories = ["builtin"]


def check(
    node: ForStmt | GeneratorExpr | DictionaryComprehension,
    errors: list[Error],
) -> None:
    check_for_loop_like(check_enumerate_call, node, errors)


def check_enumerate_call(
    index: Node, expr: Node, contexts: list[Node], errors: list[Error]
) -> None:
    match index, expr:
        case (
            TupleExpr(items=[NameExpr() as index, NameExpr() as value]),
            CallExpr(
                callee=NameExpr(fullname="builtins.enumerate"),
                args=[NameExpr(node=Var(type=ty))],
            ),
        ) if is_sequence_type(str(ty)):
            check_unused_index_or_value(index, value, contexts, errors)


def check_unused_index_or_value(
    index: NameExpr, value: NameExpr, contexts: list[Node], errors: list[Error]
) -> None:
    if is_placeholder(index) or is_name_unused_in_contexts(index, contexts):
        errors.append(
            ErrorInfo(
                index.line,
                index.column,
                "Index is unused, use `for x in y` instead",
            )
        )

    if is_placeholder(value) or is_name_unused_in_contexts(value, contexts):
        errors.append(
            ErrorInfo(
                value.line,
                value.column,
                "Value is unused, use `for x in range(len(y))` instead",
            )
        )


# TODO: allow for any type that supports the Sequence protocol
def is_sequence_type(ty: str) -> bool:
    return ty.startswith(("builtins.list[", "Tuple[", "builtins.tuple["))
