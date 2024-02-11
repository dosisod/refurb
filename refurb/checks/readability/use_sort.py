from dataclasses import dataclass

from mypy.nodes import ArgKind, AssignmentStmt, CallExpr, NameExpr

from refurb.checks.common import get_mypy_type, is_equivalent, is_same_type, stringify
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Don't use `sorted()` to sort a list and reassign it to itself, use the
    faster in-place `.sort()` method instead.

    Bad:

    ```
    names = ["Bob", "Alice", "Charlie"]

    names = sorted(names)
    ```

    Good:

    ```
    names = ["Bob", "Alice", "Charlie"]

    names.sort()
    ```
    """

    name = "use-sort"
    categories = ("performance", "readability")
    code = 186


def check(node: AssignmentStmt, errors: list[Error]) -> None:
    match node:
        case AssignmentStmt(
            lvalues=[assign_ref],
            rvalue=CallExpr(
                callee=NameExpr(fullname="builtins.sorted"),
                args=[sorted_arg, *rest],
                arg_names=[_, *arg_names],
                arg_kinds=[_, *arg_kinds],
            ),
        ) if (
            is_equivalent(assign_ref, sorted_arg)
            and is_same_type(get_mypy_type(sorted_arg), list)
            and all(arg_kind == ArgKind.ARG_NAMED for arg_kind in arg_kinds)
        ):
            new_args: list[str] = []

            name = stringify(assign_ref)

            if rest:
                for arg_name, expr in zip(arg_names, rest):
                    arg = f"{arg_name}={stringify(expr)}"

                    new_args.append(arg)

            old = stringify(node)
            new = f"{name}.sort({', '.join(new_args)})"

            msg = f"Replace `{old}` with `{new}`"

            errors.append(ErrorInfo.from_node(node, msg))
