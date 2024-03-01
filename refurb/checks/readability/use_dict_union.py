from dataclasses import dataclass
from itertools import groupby

from mypy.nodes import ArgKind, CallExpr, DictExpr, RefExpr

from refurb.checks.common import is_mapping, stringify
from refurb.error import Error
from refurb.settings import Settings


@dataclass
class ErrorInfo(Error):
    """
    Dicts can be created/combined in many ways, one of which is the `**`
    operator (inside the dict), and another is the `|` operator (used outside
    the dict). While they both have valid uses, the `|` operator allows for
    more flexibility, including using `|=` to update an existing dict.

    See PEP 584 for more info.

    Bad:

    ```
    def add_defaults(settings: dict[str, str]) -> dict[str, str]:
        return {"color": "1", **settings}
    ```

    Good:

    ```
    def add_defaults(settings: dict[str, str]) -> dict[str, str]:
        return {"color": "1"} | settings
    ```
    """

    name = "use-dict-union"
    code = 173
    categories = ("dict", "readability")


def check(node: DictExpr | CallExpr, errors: list[Error], settings: Settings) -> None:
    if settings.get_python_version() < (3, 9):
        return  # pragma: no cover

    match node:
        case DictExpr(items=items):
            groups = [(k, list(v)) for k, v in groupby(items, lambda x: x[0] is None)]

            if len(groups) not in {1, 2}:
                # Only allow groups of 1 and 2 because a group of 0 means the
                # dict is empty, and 3 or more means that there are 3 or more
                # alternations of star and non-star patterns in the dict,
                # which would look like `x | {"k": "v"} | z`, for example, and
                # to me this looks less readable. I might change this later.
                return

            if len(groups) == 1 and (not groups[0][0] or len(groups[0][1]) == 1):
                return

            old: list[str] = []
            new: list[str] = []

            index = 1

            for group in groups:
                is_star, pairs = group

                for pair in pairs:
                    if is_star:
                        _, star_expr = pair

                        if not is_mapping(star_expr):
                            return

                        old.append(f"**{stringify(star_expr)}")
                        new.append(stringify(star_expr))

                        index += 1

                    else:
                        old.append("...")
                        new.append("{...}")

            old_msg = ", ".join(old)
            new_msg = " | ".join(new)

            msg = f"Replace `{{{old_msg}}}` with `{new_msg}`"

            errors.append(ErrorInfo.from_node(node, msg))

        case CallExpr(callee=RefExpr(fullname="builtins.dict")):
            args: list[str] = []
            kwargs: dict[str, str] = {}

            # ignore dict(x) and dict() since that is covered by FURB123
            match node.arg_kinds:
                case [] | [ArgKind.ARG_POS]:
                    return

            # TODO: move dict(a=1, b=2) to FURB112
            if all(x == ArgKind.ARG_NAMED for x in node.arg_kinds):
                return

            for arg, name, kind in zip(node.args, node.arg_names, node.arg_kinds):
                # ignore dict(*x)
                if kind == ArgKind.ARG_STAR:
                    return

                if kind == ArgKind.ARG_STAR2:
                    if not is_mapping(arg):
                        return

                    stringified_arg = stringify(arg)

                    if len(node.args) == 1:
                        # TODO: dict(**x) can be replaced with x.copy() if we know x has a copy()
                        # method.
                        stringified_arg = f"{{**{stringified_arg}}}"

                    args.append(stringified_arg)

                elif name:
                    kwargs[name] = stringify(arg)

                else:
                    args.append(stringify(arg))

            old_msg = stringify(node)

            if kwargs:
                kwargs2 = ", ".join(f'"{name}": {expr}' for name, expr in kwargs.items())
                kwargs2 = f"{{{kwargs2}}}"

                args.append(kwargs2)

            new_msg = " | ".join(args)

            msg = f"Replace `{old_msg}` with `{new_msg}`"

            errors.append(ErrorInfo.from_node(node, msg))
