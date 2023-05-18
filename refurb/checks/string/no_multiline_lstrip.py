from dataclasses import dataclass

from mypy.nodes import CallExpr, MemberExpr, StrExpr

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    r'''
    If you want to define a multi-line string but don't want a leading/trailing
    newline, use a continuation character ('\') instead of calling `lstrip()`,
    `rstrip()`, or `strip()`.

    Bad:

    ```
    """
    This is some docstring
    """.lstrip()

    """
    This is another docstring
    """.strip()
    ```

    Good:

    ```
    """\
    This is some docstring
    """

    """\
    This is another docstring\
    """
    ```
    '''

    name = "no-multiline-strip"
    code = 139
    categories = ("readability",)


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=MemberExpr(
                expr=StrExpr(value=value),
                name="lstrip" | "rstrip" | "strip" as func,
            ),
            args=[] | [StrExpr(value="\n")] as args,
        ) if node.line != node.end_line and len(value) > 1:
            leading_newline = value.startswith("\n") and not value[1].isspace()
            trailing_newline = value.endswith("\n") and not value[-2].isspace()

            if func == "strip" and (leading_newline or trailing_newline):
                pass

            elif func == "lstrip" and leading_newline:
                trailing_newline = False

            elif func == "rstrip" and trailing_newline:
                leading_newline = False

            else:
                return

            func_expr: str = func
            func_expr += '("\\n")' if args else "()"

            parts = [
                '"""',
                "\\n" if leading_newline else "",
                "...",
                "\\n" if trailing_newline else "",
                '"""',
            ]

            old = "".join(parts)
            new = old.replace("n", "")

            errors.append(
                ErrorInfo.from_node(
                    node, f"Replace `{old}.{func_expr}` with `{new}`"
                )
            )
