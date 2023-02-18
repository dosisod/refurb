# these should match

_ = bin(0b1111).count("1")
_ = bin(0b0011 & 0b11).count("1")
_ = bin(1 < 2).count("1")
_ = bin(0b1111)[2:].count("1")  # noqa: FURB116

x = 0b1111
_ = bin(x).count("1")
_ = bin(int("123")).count("1")
_ = bin([1][0]).count("1")


# these should not

_ = "hello".count("1")
_ = bin(0b1111).endswith("1")
_ = bin(1, 2).count("1")  # type: ignore
_ = bin(0b1111)[3:].count("1")
_ = bin(0b1111)[2:1].count("1")
_ = bin(0b1111).count("1", 123)
