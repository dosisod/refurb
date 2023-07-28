from dataclasses import dataclass

from mypy.nodes import CallExpr, MemberExpr, RefExpr, StrExpr

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    If you want to get the current working directory don't call `resolve()` on
    an empty `Path()` object, use `Path.cwd()` instead.

    Bad:

    ```
    cwd = Path().resolve()
    ```

    Good:

    ```
    cwd = Path.cwd()
    ```
    """

    name = "no-implicit-cwd"
    code = 177
    categories = ("pathlib",)


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=MemberExpr(
                expr=CallExpr(
                    callee=RefExpr(fullname="pathlib.Path"),
                    args=[] | [StrExpr(value="" | ".")] as args,
                ),
                name="resolve",
            ),
            args=[],
        ):
            arg = f'"{args[0].value}"' if args else ""  # type: ignore
            msg = f"Replace `Path({arg}).resolve()` with `Path.cwd()`"

            errors.append(ErrorInfo.from_node(node, msg))
