# these will match

f"{str('hello world')}"  # noqa: FURB123

f"{repr(123)}"

f"{ascii('hello world')}"

f"{bin(0b1100)}"

f"{oct(0o777)}"

f"{hex(0xFF)}"

f"{chr(0x41)}"

f"{format('hello world')}"


# these will not

f"{123}"

f"{0b1010:b}"

f"{str('hello world')!s}"  # noqa: FURB123

f"{str(b'hello world', encoding='utf8')}"
