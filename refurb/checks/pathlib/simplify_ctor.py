from dataclasses import dataclass

from mypy.nodes import CallExpr, RefExpr, StrExpr

from refurb.checks.common import normalize_os_path, stringify
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    The Path() constructor defaults to the current directory, so don't pass the
    current directory explicitly.

    Bad:

    ```
    file = Path(".")
    ```

    Good:

    ```
    file = Path()
    ```

    Note: Lots of different values can trigger this check, including `"."`,
    `""`, `os.curdir`, and `os.path.curdir`.
    """

    name = "simplify-path-constructor"
    code = 153
    categories = ("pathlib", "readability")


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            args=[StrExpr(value="." | "" as value)],
            callee=RefExpr(fullname="pathlib.Path") as ref,
        ):
            func_name = stringify(ref)

            errors.append(
                ErrorInfo.from_node(node, f'Replace `{func_name}("{value}")` with `Path()`')
            )

    match node:
        case CallExpr(
            args=[RefExpr(fullname=arg) as arg_ref],
            callee=RefExpr(fullname="pathlib.Path") as func_ref,
        ) if (arg := normalize_os_path(arg)) in {"os.curdir", "os.path.curdir"}:
            func_name = stringify(func_ref)
            arg_name = stringify(arg_ref)

            msg = f"Replace `{func_name}({arg_name})` with `Path()`"

            errors.append(ErrorInfo.from_node(node, msg))
