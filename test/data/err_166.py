# these should match

_ = int("0b1010"[2:], 2)
_ = int("0o777"[2:], 8)
_ = int("0xFFFF"[2:], 16)

b = "0b11"
_ = int(b[2:], 2)

_ = int("0xFFFF"[2:], base=16)


# these should not

_ = int("0b1100", 0)
_ = int("123", 3)
_ = int("123", 10)  # noqa: FURB120
_ = int("0b1010"[3:], 2)
_ = int("0b1010"[:2], 2)
_ = int("12345"[:2])
_ = int("12345"[:2], xyz=1)  # type: ignore
