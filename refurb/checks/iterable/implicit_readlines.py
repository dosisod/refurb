from dataclasses import dataclass

from mypy.nodes import CallExpr, Expression, ForStmt, GeneratorExpr, MemberExpr

from refurb.checks.common import get_mypy_type, is_subclass, stringify
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    When iterating over a file object line-by-line you don't need to add
    `.readlines()`, simply iterate over the object itself. This assumes you
    aren't passing an argument to readlines().

    Bad:

    ```
    with open("file.txt") as f:
        for line in f.readlines():
            ...
    ```

    Good:

    ```
    with open("file.txt") as f:
        for line in f:
            ...
    ```
    """

    name = "simplify-readlines"
    code = 129
    categories = ("builtin", "readability")


def check_readline_expr(expr: Expression, errors: list[Error]) -> None:
    match expr:
        case CallExpr(
            callee=MemberExpr(expr=f, name="readlines"),
            args=[],
        ) if is_subclass(get_mypy_type(f), "io.IOBase"):
            tmp = stringify(f)

            msg = f"Replace `{tmp}.readlines()` with `{tmp}`"

            errors.append(ErrorInfo.from_node(f, msg))


def check(node: ForStmt | GeneratorExpr, errors: list[Error]) -> None:
    if isinstance(node, ForStmt):
        check_readline_expr(node.expr, errors)

    else:
        for expr in node.sequences:
            check_readline_expr(expr, errors)
