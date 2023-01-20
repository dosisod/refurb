from dataclasses import dataclass

from mypy.nodes import BytesExpr, CallExpr, MemberExpr, NameExpr, StrExpr, Var

from refurb.checks.pathlib.util import is_pathlike
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Don't use the `os.path.getsize` (or similar) functions, use the more modern
    `pathlib` module instead:

    Bad:

    ```
    if os.path.getsize("file.txt"):
        pass
    ```

    Good:

    ```
    if Path("file.txt").stat().st_size:
        pass
    ```
    """

    name = "use-pathlib-statsize-funcs"
    code = 154
    categories = ["pathlib"]


PATH_TO_PATHLIB_NAMES = {
    "posixpath.getsize": "stat().st_size",
    "genericpath.getsize": "stat().st_size",
    "ntpath.getsize": "stat().st_size",
}


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=MemberExpr(fullname=fullname, name=name),
            args=[arg],
        ) if new_name := PATH_TO_PATHLIB_NAMES.get(fullname or ""):
            if is_pathlike(arg):
                replace = f"x.{new_name}"

            else:
                match arg:
                    case BytesExpr() | StrExpr():
                        pass

                    case NameExpr(node=Var(type=ty)) if (
                        str(ty) in ("builtins.str", "builtins.bytes")
                    ):
                        pass

                    case _:
                        return

                replace = f"Path(x).{new_name}"

            errors.append(
                ErrorInfo(
                    node.line,
                    node.column,
                    f"Replace `os.path.getsize(x)` with `{replace}`",
                )
            )
