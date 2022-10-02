from dataclasses import dataclass

from mypy.nodes import CallExpr, NameExpr, StrExpr

from refurb.checks.pathlib.util import is_pathlike
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    When you want to open a Path object, don't stringify the name and pass
    it to `open()`, just call `.open()` instead:

    Bad:

    ```
    path = Path("filename")

    with open(str(path)) as f:
        pass
    ```

    Good:

    ```
    path = Path("filename")

    with path.open() as f:
        pass
    ```
    """

    code = 117


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=NameExpr(fullname="builtins.open") as open_node,
            args=[
                CallExpr(
                    callee=NameExpr(fullname="builtins.str"),
                    args=[path],
                ),
                *rest,
            ],
        ) if is_pathlike(path):
            mode = args = ""

            match rest:
                case [StrExpr(value=value), *_]:
                    mode = f'"{value}"'
                    args = f", {mode}"

            errors.append(
                ErrorInfo(
                    open_node.line,
                    open_node.column,
                    f"Use `x.open({mode})` instead of `open(str(x){args})`",
                )
            )
