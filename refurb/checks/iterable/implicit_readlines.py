from dataclasses import dataclass

from mypy.nodes import CallExpr, Expression, ForStmt, GeneratorExpr, MemberExpr, NameExpr, Var

from refurb.checks.common import stringify
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


def check_for_readline_object(expr: Expression, errors: list[Error]) -> NameExpr | None:
    match expr:
        case CallExpr(
            callee=MemberExpr(expr=NameExpr(node=Var(type=ty)) as f, name="readlines"),
            args=[],
        ) if str(ty) in {"io.TextIOWrapper", "io.BufferedReader"}:
            f_name = stringify(f)

            msg = f"Replace `{f_name}.readlines()` with `{f_name}`"

            errors.append(ErrorInfo.from_node(f, msg))

    return None


def check(node: ForStmt | GeneratorExpr, errors: list[Error]) -> None:
    if isinstance(node, ForStmt):
        check_for_readline_object(node.expr, errors)

    else:
        for expr in node.sequences:
            check_for_readline_object(expr, errors)
