from dataclasses import dataclass

from mypy.nodes import BytesExpr, CallExpr, MemberExpr, NameExpr, StrExpr, Var

from refurb.checks.common import normalize_os_path
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

    name = "use-pathlib-stat"
    code = 155
    categories = ["pathlib"]


PATH_TO_PATHLIB_NAMES = {
    "os.stat": "stat()",
    "os.path.getsize": "stat().st_size",
    "os.path.getatime": "stat().st_atime",
    "os.path.getmtime": "stat().st_mtime",
    "os.path.getctime": "stat().st_ctime",
}


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(callee=MemberExpr(fullname=fullname), args=[arg]):
            normalized_name = normalize_os_path(fullname or "")
            new_name = PATH_TO_PATHLIB_NAMES.get(normalized_name)

            if not new_name:
                return

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
                    f"Replace `{normalized_name}(x)` with `{replace}`",
                )
            )
