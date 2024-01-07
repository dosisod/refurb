from dataclasses import dataclass

from mypy.nodes import ArgKind, AssignmentStmt, CallExpr, NameExpr, Var

from refurb.checks.common import stringify, unmangle_name
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
            lvalues=[NameExpr(fullname=assign_name) as assign_ref],
            rvalue=CallExpr(
                callee=NameExpr(fullname="builtins.sorted"),
                args=[
                    NameExpr(fullname=sort_name, node=Var(type=ty)),
                    *rest,
                ],
                arg_names=[_, *arg_names],
                arg_kinds=[_, *arg_kinds],
            ),
        ) if (
            unmangle_name(assign_name) == unmangle_name(sort_name)
            and str(ty).startswith("builtins.list[")
            and all(arg_kind == ArgKind.ARG_NAMED for arg_kind in arg_kinds)
        ):
            old_args: list[str] = []
            new_args: list[str] = []

            name = stringify(assign_ref)

            old_args.append(name)

            if rest:
                for arg_name, expr in zip(arg_names, rest):
                    arg = f"{arg_name}={stringify(expr)}"

                    old_args.append(arg)
                    new_args.append(arg)

            old = f"{name} = sorted({', '.join(old_args)})"
            new = f"{name}.sort({', '.join(new_args)})"

            msg = f"Replace `{old}` with `{new}`"

            errors.append(ErrorInfo.from_node(node, msg))
