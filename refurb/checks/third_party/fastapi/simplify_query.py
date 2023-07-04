from dataclasses import dataclass

from mypy.nodes import CallExpr, EllipsisExpr, FuncDef, NameExpr

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    FastAPI will automatically pass along query parameters to your function, so
    you only need to use `Query()` when you use params other than `default`.

    Bad:

    ```
    @app.get("/")
    def index(name: str = Query()) -> str:
        return f"Your name is {name}"
    ```

    Good:

    ```
    @app.get("/")
    def index(name: str) -> str:
        return f"Your name is {name}"
    ```
    """

    name = "simplify-fastapi-query"
    code = 175
    categories = ("fastapi", "readability")


def check(node: FuncDef, errors: list[Error]) -> None:
    for arg in node.arguments:
        name = arg.variable.fullname

        match arg.initializer:
            case CallExpr(
                callee=NameExpr(fullname="fastapi.param_functions.Query"),
                args=query_args,
                arg_names=query_arg_names,
            ):
                if len(query_arg_names) > 1:
                    continue

                ty = ": T" if arg.type_annotation else ""
                is_ellipsis = False

                if query_arg_names:
                    # Query(...) is special in that it acts the same as Query()
                    # so keep track of this so we can emit a better message.
                    is_ellipsis = isinstance(query_args[0], EllipsisExpr)

                    query_arg = "..." if is_ellipsis else "x"

                    if query_arg_names[0] == "default":
                        query = f"Query(default={query_arg})"

                    elif query_arg_names[0] is None:
                        query = f"Query({query_arg})"

                    else:
                        continue

                else:
                    query = "Query()"

                old = f"{name}{ty} = {query}"
                new = f"{name}{ty}" if is_ellipsis else f"{name}{ty} = x"

                msg = f"Replace `{old}` with `{new}`"

                errors.append(ErrorInfo.from_node(arg, msg))
