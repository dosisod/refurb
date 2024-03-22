from dataclasses import dataclass

from mypy.nodes import CallExpr, IndexExpr, IntExpr, MemberExpr, NameExpr, RefExpr, SliceExpr

from refurb.checks.common import is_none_literal, stringify
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Depending on how you are using the `secrets` module, there might be more
    expressive ways of writing what it is you're trying to write.

    Bad:

    ```
    random_hex = token_bytes().hex()
    random_url = token_urlsafe()[:16]
    ```

    Good:

    ```
    random_hex = token_hex()
    random_url = token_urlsafe(16)
    ```
    """

    name = "simplify-token-function"
    code = 174
    categories = ("readability", "secrets")


def check(node: CallExpr | IndexExpr, errors: list[Error]) -> None:
    match node:
        # Detects `token_bytes().hex()`
        case CallExpr(
            callee=MemberExpr(
                expr=CallExpr(
                    callee=RefExpr(fullname="secrets.token_bytes") as ref,
                    args=token_args,
                ),
                name="hex",
            ),
            args=[],
        ):
            match token_args:
                case [IntExpr(value=value)]:
                    arg = str(value)

                case [arg] if is_none_literal(arg):
                    arg = "None"

                case []:
                    arg = ""

                case _:
                    return

            new_arg = "" if arg == "None" else arg
            prefix = "secrets." if isinstance(ref, MemberExpr) else ""
            old = f"{prefix}token_bytes({arg}).hex()"
            new = f"{prefix}token_hex({new_arg})"

            msg = f"Replace `{old}` with `{new}`"

            errors.append(ErrorInfo.from_node(node, msg))

        # Detects `token_xyz()[:x]`
        case IndexExpr(
            base=CallExpr(
                callee=RefExpr(
                    fullname=fullname,
                    name=name,  # type: ignore[misc]
                ) as ref,
                args=[] | [NameExpr(fullname="builtins.None")] as args,
            ),
            index=SliceExpr(
                begin_index=None,
                end_index=IntExpr(value=size),
                stride=None,
            ),
        ) if fullname in {"secrets.token_hex", "secrets.token_bytes"}:
            arg = "None" if args else ""
            func_name = stringify(ref)

            old = f"{func_name}({arg})[:{size}]"

            # size must be multiple of 2 for hex functions since each hex digit
            # takes up 2 bytes.
            if name == "token_hex":
                if size % 2 == 1:
                    return

                size //= 2

            new = f"{func_name}({size})"

            msg = f"Replace `{old}` with `{new}`"

            errors.append(ErrorInfo.from_node(node, msg))
