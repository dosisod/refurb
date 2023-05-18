from dataclasses import dataclass

from mypy.nodes import CallExpr, RefExpr, Var

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    If you are passing a compiled regular expression to a regex function,
    consider calling the regex method on the pattern itself: It is faster, and
    can improve readability.

    Bad:

    ```
    import re

    COMMENT = re.compile(".*(#.*)")

    found_comment = re.match(COMMENT, "this is a # comment")
    ```

    Good:

    ```
    import re

    COMMENT = re.compile(".*(#.*)")

    found_comment = COMMENT.match("this is a # comment")
    ```
    """

    name = "use-regex-pattern-methods"
    code = 170
    categories = ("readability", "regex")


# This table represents the function calls that we will emit errors for. The
# ellipsis are positional args, and the strings are optional args/kwargs.
# The number of required/optional args must match, and if an optional arg
# is used, it must either be unnamed (positional), or named (kwarg), and if
# so, must match the string name.
REGEX_FUNC_ARGS = {
    "re.search": (..., ...),
    "re.match": (..., ...),
    "re.fullmatch": (..., ...),
    "re.split": (..., ..., "maxsplit"),
    "re.findall": (..., ...),
    "re.finditer": (..., ...),
    "re.sub": (..., ..., ..., "count"),
    "re.subn": (..., ..., ..., "count"),
}


def build_args(arg_names: list[str | None]) -> str:
    args = ["..." if arg is None else f"{arg}=..." for arg in arg_names]

    return ", ".join(args)


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=RefExpr(fullname=fullname, name=name),  # type: ignore
            args=[pattern, *_] as args,
            arg_names=arg_names,
        ):
            arg_format = REGEX_FUNC_ARGS.get(fullname)

            if not arg_format:
                return

            match pattern:
                case RefExpr(node=Var(type=ty)) if (
                    str(ty).startswith("re.Pattern[")
                ):
                    pass

                case _:
                    return

            min_len = len([arg for arg in arg_format if arg is ...])

            if len(args) < min_len or len(args) > len(arg_format):
                return

            if isinstance(arg_format[-1], str):
                if arg_names[-1] and arg_names[-1] != arg_format[-1]:
                    return

            params = build_args(arg_names[1:])

            msg = f"Replace `{fullname}(x, {params})` with `x.{name}({params})`"  # noqa: E501

            errors.append(ErrorInfo.from_node(node, msg))
