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

from refurb.checks.common import check_for_loop_like, is_name_unused_in_contexts, stringify
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
    categories = ("builtin",)


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
                args=[NameExpr(node=Var(type=ty)) as enumerate_arg],
            ),
        ) if is_sequence_type(str(ty)):
            check_unused_index_or_value(index, value, contexts, errors, enumerate_arg)


def check_unused_index_or_value(
    index: NameExpr,
    value: NameExpr,
    contexts: list[Node],
    errors: list[Error],
    enumerate_arg: NameExpr,
) -> None:
    if is_name_unused_in_contexts(index, contexts):
        msg = f"Index is unused, use `for {stringify(value)} in {stringify(enumerate_arg)}` instead"  # noqa: E501

        errors.append(ErrorInfo.from_node(index, msg))

    if is_name_unused_in_contexts(value, contexts):
        msg = f"Value is unused, use `for {stringify(index)} in range(len({stringify(enumerate_arg)}))` instead"  # noqa: E501

        errors.append(ErrorInfo.from_node(value, msg))


# TODO: allow for any type that supports the Sequence protocol
def is_sequence_type(ty: str) -> bool:
    return ty.startswith(("builtins.list[", "Tuple[", "builtins.tuple[", "tuple["))
