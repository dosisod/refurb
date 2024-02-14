from dataclasses import dataclass

from mypy.nodes import CallExpr, RefExpr

from refurb.checks.common import get_mypy_type, is_same_type, normalize_os_path
from refurb.checks.pathlib.util import is_pathlike
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Don't use the `os.path.isfile` (or similar) functions, use the more modern
    `pathlib` module instead:

    Bad:

    ```
    if os.path.isfile("file.txt"):
        pass
    ```

    Good:

    ```
    if Path("file.txt").is_file():
        pass
    ```
    """

    name = "use-pathlib-is-funcs"
    code = 146
    categories = ("pathlib",)


PATH_TO_PATHLIB_NAMES = {
    "os.path.isabs": "is_absolute",
    "os.path.isdir": "is_dir",
    "os.path.isfile": "is_file",
    "os.path.islink": "is_symlink",
}


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(callee=RefExpr(fullname=fullname), args=[arg]):
            normalized_name = normalize_os_path(fullname)
            new_name = PATH_TO_PATHLIB_NAMES.get(normalized_name)

            if not new_name:
                return

            if is_pathlike(arg):
                new = f"x.{new_name}()"

            elif is_same_type(get_mypy_type(arg), str, bytes):
                new = f"Path(x).{new_name}()"

            else:
                return

            msg = f"Replace `{normalized_name}(x)` with `{new}`"

            errors.append(ErrorInfo.from_node(node, msg))
