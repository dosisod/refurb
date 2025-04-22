from dataclasses import dataclass

from mypy.nodes import (
    CallExpr,
    Expression,
    GeneratorExpr,
    ListComprehension,
    MemberExpr,
    NameExpr,
    Node,
    RefExpr,
    StrExpr,
)

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    When using `shlex` to escape and join a bunch of strings consider using the
    `shlex.join` method instead.

    Bad:

    ```
    args = ["hello", "world!"]

    cmd = " ".join(shlex.quote(arg) for arg in args)
    ```

    Good:

    ```
    args = ["hello", "world!"]

    cmd = shlex.join(args)
    ```
    """

    name = "use-shlex-join"
    code = 178
    categories = ("readability", "shlex")


def handle_join_arg(root: Node, arg: Expression) -> list[Error]:
    match arg:
        case GeneratorExpr(
            left_expr=CallExpr(
                callee=RefExpr(fullname="shlex.quote") as ref,
                args=[quote_arg],
            ),
            condlists=[condlist],
        ):
            if isinstance(ref, MemberExpr):
                quote = "shlex.quote"
                join = "shlex.join"

            else:
                quote = ref.name  # type: ignore
                join = "join"

            if isinstance(quote_arg, NameExpr) and not condlist:
                old = f'" ".join({quote}(x) for x in y)'
                new = f"{join}(y)"

            else:
                if_expr = " if ..." if condlist else ""

                old = f'" ".join({quote}(...) for x in y{if_expr})'
                new = f"{join}(... for x in y{if_expr})"

            msg = f"Replace `{old}` with `{new}`"

            return [ErrorInfo.from_node(root, msg)]

        case ListComprehension():
            return handle_join_arg(root, arg.generator)

    return []


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=MemberExpr(
                expr=StrExpr(value=" "),
                name="join",
            ),
            args=[arg],
        ):
            errors += handle_join_arg(node, arg)
