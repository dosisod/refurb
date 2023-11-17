from dataclasses import dataclass

from mypy.nodes import ClassDef, NameExpr, RefExpr

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Instead of setting `metaclass` directly, inherit from the `ABC` wrapper
    class. This is semantically the same thing, but more succinct.

    Bad:

    ```
    class C(metaclass=ABCMeta):
        pass
    ```

    Good:

    ```
    class C(ABC):
        pass
    ```
    """

    name = "use-abc-shorthand"
    code = 180
    categories = ("abc", "readability")


def check(node: ClassDef, errors: list[Error]) -> None:
    match node:
        case ClassDef(metaclass=RefExpr(fullname="abc.ABCMeta") as ref):
            metaclass = node.metaclass
            assert metaclass

            # HACK: attempt to calculate the start of the metaclass keyword
            # from the position of its argument
            column = metaclass.column - 10
            column_end = metaclass.end_column - 10 if metaclass.end_column else None

            prefix = "" if isinstance(ref, NameExpr) else "abc."

            msg = f"Replace `metaclass={prefix}ABCMeta` with `{prefix}ABC`"

            errors.append(
                ErrorInfo(
                    line=metaclass.line,
                    column=column,
                    line_end=metaclass.end_line,
                    column_end=column_end,
                    msg=msg,
                )
            )
