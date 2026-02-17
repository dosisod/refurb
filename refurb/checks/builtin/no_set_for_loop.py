from dataclasses import dataclass

from mypy.nodes import Block, CallExpr, Expression, ExpressionStmt, ForStmt, IndexExpr, MemberExpr, NameExpr

from refurb.checks.common import get_mypy_type, is_equivalent, is_same_type, stringify
from refurb.error import Error


def _references_name(node: Expression, name: NameExpr) -> bool:
    """Check if an expression tree contains a reference to the given name."""
    if isinstance(node, NameExpr):
        return is_equivalent(node, name)
    if isinstance(node, MemberExpr):
        return _references_name(node.expr, name)
    if isinstance(node, IndexExpr):
        return _references_name(node.base, name) or _references_name(node.index, name)
    if isinstance(node, CallExpr):
        return _references_name(node.callee, name) or any(_references_name(a, name) for a in node.args)
    return False


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
    categories = ("builtin",)


def check(node: ForStmt, errors: list[Error]) -> None:
    match node:
        case ForStmt(
            index=NameExpr() as index,
            expr=source,
            body=Block(
                body=[
                    ExpressionStmt(
                        expr=CallExpr(
                            callee=MemberExpr(expr=set_expr, name=("add" | "discard") as name),
                            args=[arg],
                        )
                    ),
                ]
            ),
            else_body=None,
            is_async=False,
        ) if is_same_type(get_mypy_type(set_expr), set) and not _references_name(set_expr, index):
            new_func = "update" if name == "add" else "difference_update"

            source = stringify(source)  # type: ignore
            set_expr = stringify(set_expr)  # type: ignore

            if isinstance(arg, NameExpr):
                if not is_equivalent(index, arg):
                    return

                old = stringify(node)
                new = f"{set_expr}.{new_func}({source})"

            else:
                index = stringify(index)  # type: ignore

                old = f"for {index} in {source}: {set_expr}.{name}(...)"
                new = f"{set_expr}.{new_func}(... for {index} in {source})"

            msg = f"Replace `{old}` with `{new}`"

            errors.append(ErrorInfo.from_node(node, msg))
