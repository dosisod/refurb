from dataclasses import dataclass

from mypy.nodes import CallExpr, Expression, MemberExpr

from refurb.checks.common import get_mypy_type, is_same_type, stringify
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
    "hashlib._BlakeHash",
    "hashlib._VarLenHash",
    "_hashlib.HASH",  # generic hashlib wrapper
    "_hashlib.HASHXOF",  # SHAKE hashes
    "_blake2.blake2b",
    "_blake2.blake2s",
    "_hashlib.openssl_md5",
    "_hashlib.openssl_sha1",
    "_hashlib.openssl_sha224",
    "_hashlib.openssl_sha256",
    "_hashlib.openssl_sha384",
    "_hashlib.openssl_sha3_224",
    "_hashlib.openssl_sha3_256",
    "_hashlib.openssl_sha3_384",
    "_hashlib.openssl_sha3_512",
    "_hashlib.openssl_sha512",
    "_hashlib.openssl_shake_128",
    "_hashlib.openssl_shake_256",
}


def is_hashlib_algo(expr: Expression) -> bool:
    return is_same_type(get_mypy_type(expr), *HASHLIB_ALGOS)


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
