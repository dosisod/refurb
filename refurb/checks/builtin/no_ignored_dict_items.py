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

from refurb.checks.common import ReadCountVisitor
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

    code = 135
    categories = ["dict"]


def check(
    node: ForStmt | GeneratorExpr | DictionaryComprehension,
    errors: list[Error],
) -> None:
    match node:
        case ForStmt(index=index, expr=expr):
            check_for_loop_like(index, expr, node.body, errors)

        case GeneratorExpr(indices=[index], sequences=[expr]):
            check_for_loop_like(index, expr, None, errors)

        case DictionaryComprehension(indices=[index], sequences=[expr]):
            check_for_loop_like(index, expr, None, errors)


def check_for_loop_like(
    index: Node, expr: Node, ctx: Node | None, errors: list[Error]
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
            check_unused_key_or_value(key, value, ctx, errors)


def check_unused_key_or_value(
    key: NameExpr, value: NameExpr, node: Node | None, errors: list[Error]
) -> None:
    if is_placeholder(key) or is_name_unused_in_context(key, node):
        errors.append(
            ErrorInfo(
                key.line,
                key.column,
                "Key is unused, use `for value in d.values()` instead",
            )
        )

    if is_placeholder(value) or is_name_unused_in_context(value, node):
        errors.append(
            ErrorInfo(
                value.line,
                value.column,
                "Value is unused, use `for key in d` instead",
            )
        )


def is_placeholder(name: NameExpr) -> bool:
    return name.name == "_"


def is_name_unused_in_context(name: NameExpr, ctx: Node | None) -> bool:
    if ctx:
        key_visitor = ReadCountVisitor(name)
        ctx.accept(key_visitor)

        return not key_visitor.was_read

    return False
