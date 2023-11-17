from dataclasses import dataclass

from mypy.nodes import CallExpr, Expression, MemberExpr, NameExpr, RefExpr, Var

from refurb.checks.common import stringify
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Use `.hexdigest()` to get a hex digest from a hash.

    Bad:

    ```
    from hashlib import sha512

    hashed = sha512(b"some data").digest().hex()
    ```

    Good:

    ```
    from hashlib import sha512

    hashed = sha512(b"some data").hexdigest()
    ```
    """

    name = "use-hexdigest-hashlib"
    categories = ("hashlib", "readability")
    code = 181


HASHLIB_ALGOS = {
    "hashlib.md5",
    "hashlib.sha1",
    "hashlib.sha224",
    "hashlib.sha256",
    "hashlib.sha384",
    "hashlib.sha512",
    "hashlib.blake2b",
    "hashlib.blake2s",
    "hashlib.sha3_224",
    "hashlib.sha3_256",
    "hashlib.sha3_384",
    "hashlib.sha3_512",
    "hashlib.shake_128",
    "hashlib.shake_256",
    "hashlib._Hash",
}


def is_hashlib_algo(expr: Expression) -> bool:
    match expr:
        case CallExpr(callee=RefExpr(fullname=fn)) if fn in HASHLIB_ALGOS:
            return True

        case NameExpr(node=Var(type=ty)) if str(ty) in HASHLIB_ALGOS:
            return True

    return False


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=MemberExpr(
                expr=CallExpr(
                    callee=MemberExpr(expr=expr, name="digest"),
                    args=[] | [_] as digest_args,
                ),
                name="hex",
            ),
            args=[],
        ):
            if is_hashlib_algo(expr):
                root = stringify(expr)

                arg = stringify(digest_args[0]) if digest_args else ""

                old = f"{root}.digest({arg}).hex()"
                new = f"{root}.hexdigest({arg})"

                msg = f"Replace `{old}` with `{new}`"
                errors.append(ErrorInfo.from_node(node, msg))
