from dataclasses import dataclass

from mypy.nodes import (
    AssignmentStmt,
    Block,
    CallExpr,
    DictionaryComprehension,
    Expression,
    ForStmt,
    GeneratorExpr,
    MypyFile,
    NameExpr,
    Node,
    Statement,
    TupleExpr,
)

from refurb.checks.common import (
    ReadCountVisitor,
    check_block_like,
    check_for_loop_like,
    get_mypy_type,
    is_name_unused_in_contexts,
    is_subclass,
    stringify,
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
    categories = ("builtin",)


def _assigns_name(stmt: Statement, name: NameExpr) -> bool:
    """Check if a statement assigns to the given name."""
    match stmt:
        case ForStmt(index=index):
            return _node_contains_name(index, name)
        case AssignmentStmt(lvalues=lvalues):
            return any(_node_contains_name(lv, name) for lv in lvalues)
    return False


def _node_contains_name(node: Node, name: NameExpr) -> bool:
    """Check if a node contains a NameExpr with the same fullname."""
    visitor = ReadCountVisitor(name)
    visitor.accept(node)
    return bool(visitor.was_read)


def _is_name_read_after_loop(name: NameExpr, remaining_stmts: list[Statement]) -> bool:
    """Check if name is read in statements after the loop, stopping at reassignment."""
    for stmt in remaining_stmts:
        if _assigns_name(stmt, name):
            # Name is reassigned — reads after this point don't count
            # as uses of the loop variable. But check the RHS first.
            rhs: Expression | None = None
            if isinstance(stmt, AssignmentStmt):
                rhs = stmt.rvalue
            elif isinstance(stmt, ForStmt):
                rhs = stmt.expr

            if rhs is not None:
                visitor = ReadCountVisitor(name)
                visitor.accept(rhs)
                if visitor.was_read:
                    return True

            return False

        # Check if name is read in this statement
        visitor = ReadCountVisitor(name)
        visitor.accept(stmt)
        if visitor.was_read:
            return True

    return False


def check(
    node: Block | MypyFile | GeneratorExpr | DictionaryComprehension,
    errors: list[Error],
) -> None:
    match node:
        case GeneratorExpr() | DictionaryComprehension():
            check_for_loop_like(check_enumerate_call, node, errors)

        case Block() | MypyFile():
            check_block_like(check_stmts_for_enumerate, node, errors)


def check_stmts_for_enumerate(stmts: list[Statement], errors: list[Error]) -> None:
    for i, stmt in enumerate(stmts):
        if not isinstance(stmt, ForStmt):
            continue

        match stmt.index, stmt.expr:
            case (
                TupleExpr(items=[NameExpr() as index, NameExpr() as value]),
                CallExpr(
                    callee=NameExpr(fullname="builtins.enumerate"),
                    args=[enumerate_arg],
                ),
            ) if is_subclass(get_mypy_type(enumerate_arg), "typing.Sequence"):
                remaining = stmts[i + 1 :]
                check_unused_index_or_value_in_block(
                    index, value, stmt.body, remaining, errors, enumerate_arg
                )


def check_enumerate_call(
    index: Node, expr: Node, contexts: list[Node], errors: list[Error]
) -> None:
    match index, expr:
        case (
            TupleExpr(items=[NameExpr() as index, NameExpr() as value]),
            CallExpr(
                callee=NameExpr(fullname="builtins.enumerate"),
                args=[enumerate_arg],
            ),
        ) if is_subclass(get_mypy_type(enumerate_arg), "typing.Sequence"):
            check_unused_index_or_value(index, value, contexts, errors, enumerate_arg)


def check_unused_index_or_value(
    index: NameExpr,
    value: NameExpr,
    contexts: list[Node],
    errors: list[Error],
    enumerate_arg: Expression,
) -> None:
    if is_name_unused_in_contexts(index, contexts):
        msg = f"Index is unused, use `for {stringify(value)} in {stringify(enumerate_arg)}` instead"  # noqa: E501

        errors.append(ErrorInfo.from_node(index, msg))

    if is_name_unused_in_contexts(value, contexts):
        msg = f"Value is unused, use `for {stringify(index)} in range(len({stringify(enumerate_arg)}))` instead"  # noqa: E501

        errors.append(ErrorInfo.from_node(value, msg))


def check_unused_index_or_value_in_block(  # noqa: PLR0913, PLR0917
    index: NameExpr,
    value: NameExpr,
    body: Node,
    remaining_stmts: list[Statement],
    errors: list[Error],
    enumerate_arg: Expression,
) -> None:
    index_unused_in_body = is_name_unused_in_contexts(index, [body])
    value_unused_in_body = is_name_unused_in_contexts(value, [body])

    if index_unused_in_body and not _is_name_read_after_loop(index, remaining_stmts):
        msg = f"Index is unused, use `for {stringify(value)} in {stringify(enumerate_arg)}` instead"  # noqa: E501
        errors.append(ErrorInfo.from_node(index, msg))

    if value_unused_in_body and not _is_name_read_after_loop(value, remaining_stmts):
        msg = f"Value is unused, use `for {stringify(index)} in range(len({stringify(enumerate_arg)}))` instead"  # noqa: E501
        errors.append(ErrorInfo.from_node(value, msg))
