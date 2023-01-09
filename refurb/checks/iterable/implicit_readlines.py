from dataclasses import dataclass

from mypy.nodes import (
    CallExpr,
    Expression,
    ForStmt,
    GeneratorExpr,
    MemberExpr,
    NameExpr,
    Var,
)

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
    msg: str = "Replace `f.readlines()` with `f`"
    categories = ["builtin", "readability"]


def get_readline_file_object(expr: Expression) -> NameExpr | None:
    match expr:
        case CallExpr(
            callee=MemberExpr(
                expr=NameExpr(node=Var(type=ty)) as f, name="readlines"
            ),
            args=[],
        ) if str(ty) in ("io.TextIOWrapper", "io.BufferedReader"):
            return f

    return None


def check(node: ForStmt | GeneratorExpr, errors: list[Error]) -> None:
    if isinstance(node, ForStmt):
        if f := get_readline_file_object(node.expr):
            errors.append(ErrorInfo(f.line, f.column))

    else:
        for expr in node.sequences:
            if f := get_readline_file_object(expr):
                errors.append(ErrorInfo(f.line, f.column))
