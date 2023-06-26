import secrets
from secrets import token_bytes, token_hex

# these should match

token_bytes(32).hex()
token_bytes(None).hex()  # noqa: FURB120
token_bytes().hex()
secrets.token_bytes().hex()

token_bytes()[:8]
token_hex()[:8]
token_bytes(None)[:8]  # noqa: FURB120
token_hex(None)[:8]  # noqa: FURB120
secrets.token_bytes()[:8]


# these should not

token_hex()[:5]

bytes().hex()  # noqa: FURB112

n = 32
token_bytes(n).hex()

token_bytes().hex("_")
