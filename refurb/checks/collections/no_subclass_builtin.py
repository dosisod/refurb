from dataclasses import dataclass

from mypy.nodes import ClassDef, NameExpr

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Subclassing `dict`, `list`, or `str` objects can be error prone, use the
    `UserDict`, `UserList`, and `UserStr` objects from the `collections` module
    instead.

    Bad:

    ```
    class CaseInsensitiveDict(dict):
        ...
    ```

    Good:

    ```
    from collections import UserDict

    class CaseInsensitiveDict(UserDict):
        ...
    ```

    Note: `isinstance()` checks for `dict`, `list`, and `str` types will fail
    when using the corresponding User class. If you need to pass custom `dict`
    or `list` objects to code you don't control, ignore this check. If you do
    control the code, consider using the following type checks instead:

    * `dict` -> `collections.abc.MutableMapping`
    * `list` -> `collections.abc.MutableSequence`
    * `str` -> No such conversion exists
    """

    enabled = False
    name = "no-subclass-builtin"
    code = 189
    categories = ("collections",)


CLASS_MAPPING = {
    "builtins.dict": "UserDict",
    "builtins.list": "UserList",
    "builtins.str": "UserStr",
}


def check(node: ClassDef, errors: list[Error]) -> None:
    match node:
        case ClassDef(
            name=class_name,
            base_type_exprs=[NameExpr(fullname=fullname, name=builtin_name)],
        ) if new_class := CLASS_MAPPING.get(fullname):
            old = f"class {class_name}({builtin_name}):"
            new = f"class {class_name}({new_class}):"
            msg = f"Replace `{old}` with `{new}`"

            errors.append(ErrorInfo.from_node(node, msg))
