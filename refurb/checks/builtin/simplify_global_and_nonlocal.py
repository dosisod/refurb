from dataclasses import dataclass

from mypy.nodes import Block, GlobalDecl, NonlocalDecl

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    The `global` and `nonlocal` keywords can take multiple comma-separated
    names, removing the need for multiple lines.

    Bad:

    ```
    def some_func():
        global x
        global y

        print(x, y)
    ```

    Good:

    ```
    def some_func():
        global x, y

        print(x, y)
    ```
    """

    name = "simplify-global-and-nonlocal"
    code = 154
    categories = ["builtin", "readability"]


def emit_error_if_needed(
    found: list[GlobalDecl | NonlocalDecl], errors: list[Error]
) -> None:
    if len(found) < 2:
        return

    name = "global" if isinstance(found[0], GlobalDecl) else "nonlocal"

    replace_lines = [f"{name} x", f"{name} y"]
    new_args = ["x", "y"]

    if len(found) >= 3:
        replace_lines.append("...")
        new_args.append("...")

    replace = "; ".join(replace_lines)
    new = f"{name} {', '.join(new_args)}"

    errors.append(
        ErrorInfo(
            found[0].line,
            found[0].column,
            f"Replace `{replace}` with `{new}`",
        )
    )


def check(node: Block, errors: list[Error]) -> None:
    found: list[GlobalDecl | NonlocalDecl] = []

    for stmt in node.body:
        if isinstance(stmt, GlobalDecl | NonlocalDecl):
            if not found or isinstance(stmt, type(found[0])):
                found.append(stmt)
                continue

        emit_error_if_needed(found, errors)
        found = []

        if isinstance(stmt, GlobalDecl | NonlocalDecl):
            found.append(stmt)

    emit_error_if_needed(found, errors)
