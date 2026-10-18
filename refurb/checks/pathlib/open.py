from dataclasses import dataclass

from mypy.nodes import ArgKind, CallExpr, NameExpr

from refurb.checks.common import stringify
from refurb.checks.pathlib.util import is_pathlike
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    When you want to open a Path object, don't pass it to `open()`, just call
    `.open()` on the Path object itself:

    Bad:

    ```
    path = Path("filename")

    with open(path) as f:
        pass
    ```

    Good:

    ```
    path = Path("filename")

    with path.open() as f:
        pass
    ```
    """

    name = "use-pathlib-open"
    code = 117
    categories = ("pathlib",)


# The parameters of `open()` that come after `file` and that `Path.open()` also
# accepts, in positional order. `closefd` and `opener` have no equivalent.
PATH_OPEN_PARAMS = ("mode", "buffering", "encoding", "errors", "newline")


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=NameExpr(fullname="builtins.open") as open_node,
            args=[
                CallExpr(
                    callee=NameExpr(fullname="builtins.str"),
                    args=[arg],
                )
                | arg,
                *rest,
            ],
        ) if is_pathlike(arg):
            open_args: list[str] = []

            for i, (name, kind, value) in enumerate(
                zip(node.arg_names[1:], node.arg_kinds[1:], rest, strict=True)
            ):
                if kind == ArgKind.ARG_POS and i < len(PATH_OPEN_PARAMS):
                    open_args.append(stringify(value))

                elif kind == ArgKind.ARG_NAMED and name in PATH_OPEN_PARAMS:
                    open_args.append(f"{name}={stringify(value)}")

                else:
                    # `closefd`, `opener`, or `*args`/`**kwargs` that might hold them
                    return

            args = "".join(f", {x}" for x in open_args)

            inner = stringify(arg)
            expr = inner if arg == node.args[0] else f"str({inner})"

            msg = f"Replace `open({expr}{args})` with `{inner}.open({', '.join(open_args)})`"

            errors.append(ErrorInfo.from_node(open_node, msg))
