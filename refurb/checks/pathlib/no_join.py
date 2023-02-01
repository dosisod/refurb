from dataclasses import dataclass

from mypy.nodes import BytesExpr, CallExpr, MemberExpr, StrExpr

from refurb.checks.common import normalize_os_path
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    When joining strings to make a filepath, use the more modern and flexible
    `Path()` object instead of `os.path.join`:

    Bad:

    ```
    with open(os.path.join("folder", "file"), "w") as f:
        f.write("hello world!")
    ```

    Good:

    ```
    from pathlib import Path

    with open(Path("folder", "file"), "w") as f:
        f.write("hello world!")

    # even better ...

    with Path("folder", "file").open("w") as f:
        f.write("hello world!")

    # even better ...

    Path("folder", "file").write_text("hello world!")
    ```

    Note that this check is disabled by default because `Path()` returns a Path
    object, not a string, meaning that the Path object will propogate throught
    your code. This might be what you want, and might encourage you to use the
    pathlib module in more places, but since it is not a drop-in replacement it
    is disabled by default.
    """

    name = "no-path-join"
    enabled = False
    code = 147
    categories = ["pathlib"]


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=MemberExpr(fullname=fullname),
            args=args,
        ) if args and normalize_os_path(fullname or "") == "os.path.join":
            trailing_dot_dot_args: list[str] = []

            for arg in reversed(args):
                if isinstance(arg, StrExpr | BytesExpr) and arg.value == "..":
                    trailing_dot_dot_args.append(
                        '".."' if isinstance(arg, StrExpr) else 'b".."'
                    )

                else:
                    break

            normal_arg_count = len(args) - len(trailing_dot_dot_args)

            if normal_arg_count <= 3:
                placeholders = ["x", "y", "z"][:normal_arg_count]

                join_args = ", ".join(placeholders + trailing_dot_dot_args)

                path_args = ", ".join(placeholders)
                parents = ".parent" * len(trailing_dot_dot_args)
                new = f"Path({path_args}){parents}"

            else:
                join_args = "..."
                new = "Path(...)"

            errors.append(
                ErrorInfo(
                    node.line,
                    node.column,
                    f"Replace `os.path.join({join_args})` with `{new}`",
                )
            )
