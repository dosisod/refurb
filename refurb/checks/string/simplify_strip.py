from dataclasses import dataclass

from mypy.nodes import CallExpr, MemberExpr, NameExpr, StrExpr, Var

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    In some situations the `.lstrip()`, `.rstrip()` and `.strip()` string
    methods can be written more succinctly: `strip()` is the same thing as
    calling both `lstrip()` and `rstrip()` together, and all the strip
    functions take an iterable argument of the characters to strip, meaning
    you don't need to call a strip function multiple times with different
    arguments, you can just concatenate them and call it once.

    Bad:

    ```
    name = input().lstrip().rstrip()

    num = "  -123".lstrip(" ").lstrip("-")
    ```

    Good:

    ```
    name = input().strip()

    num = "  -123".lstrip(" -")
    ```
    """

    name = "simplify-strip"
    code = 159
    categories = ("readability", "string")


STRIP_FUNCS = ("lstrip", "rstrip", "strip")


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=MemberExpr(
                expr=CallExpr(
                    callee=MemberExpr(expr=expr, name=lhs_func),
                    args=lhs_args,
                ),
                name=rhs_func,
            ),
            args=rhs_args,
        ) if rhs_func in STRIP_FUNCS and lhs_func in STRIP_FUNCS:
            match expr:
                case StrExpr():
                    pass

                case NameExpr(node=Var(type=ty)) if str(ty) == "builtins.str":
                    pass

                case _:
                    return

            exprs: list[str]

            match lhs_args, rhs_args:
                case [], []:
                    lhs_arg = rhs_arg = ""

                    if lhs_func == rhs_func:
                        exprs = [f"{lhs_func}()"]
                    else:
                        exprs = ["strip()"]

                case (
                    [StrExpr(value=lhs_arg)],
                    [StrExpr(value=rhs_arg)],
                ):
                    if lhs_func == rhs_func:
                        combined = "".join(sorted(set(lhs_arg + rhs_arg)))
                        exprs = [f"{lhs_func}({combined!r})"]

                    elif lhs_arg == rhs_arg:
                        exprs = [f"strip({lhs_arg!r})"]

                    else:
                        return

                    lhs_arg = repr(lhs_arg)
                    rhs_arg = repr(rhs_arg)

                case _:
                    return

            lhs = f"{lhs_func}({lhs_arg})"
            rhs = f"{rhs_func}({rhs_arg})"
            new = f"x.{'.'.join(exprs)}"

            errors.append(
                ErrorInfo.from_node(
                    node, f"Replace `x.{lhs}.{rhs}` with `{new}`"
                )
            )
