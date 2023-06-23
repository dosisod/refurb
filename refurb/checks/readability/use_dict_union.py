from dataclasses import dataclass
from itertools import groupby

from mypy.nodes import DictExpr

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


def check(node: DictExpr, errors: list[Error], settings: Settings) -> None:
    if settings.get_python_version() < (3, 9):
        return  # pragma: no cover

    match node:
        case DictExpr(items=items):
            groups = [
                (k, list(v)) for k, v in groupby(items, lambda x: x[0] is None)
            ]

            if len(groups) not in (1, 2):
                # Only allow groups of 1 and 2 because a group of 0 means the
                # dict is empty, and 3 or more means that there are 3 or more
                # alternations of star and non-star patterns in the dict,
                # which would look like `x | {"k": "v"} | z`, for example, and
                # to me this looks less readable. I might change this later.
                return

            if len(groups) == 1 and (
                not groups[0][0] or len(groups[0][1]) == 1
            ):
                return

            old: list[str] = []
            new: list[str] = []

            index = 1

            for group in groups:
                is_star, pairs = group

                for _ in pairs:
                    if is_star:
                        old.append(f"**x{index}")
                        new.append(f"x{index}")

                        index += 1

                    else:
                        old.append("...")
                        new.append("{...}")

            # Hack to keep list sorted while removing neighboring duplicates
            unique_unsorted = dict.fromkeys

            old_msg = ", ".join(unique_unsorted(old))
            new_msg = " | ".join(unique_unsorted(new))

            msg = f"Replace `{{{old_msg}}}` with `{new_msg}`"

            errors.append(ErrorInfo.from_node(node, msg))
