# these will match

_ = bool(True)
_ = bytes(b"hello world")
_ = complex(1j)
_ = dict({"a": 1})
_ = float(123.456)
_ = list([1, 2, 3])
_ = str("hello world")
_ = tuple((1, 2, 3))
_ = int(123)

a = True
_ = bool(a)

b = b"hello world"
_ = bytes(b)

c = 1j
_ = complex(c)

d = {"a": 1}
_ = dict(d)

e = 123.456
_ = float(e)

f = [1, 2, 3]
_ = list(f)

g = "hello world"
_ = str(g)

t = (1, 2, 3)
_ = tuple(t)


# these will not

_ = bool([])
_ = bytes(0xFF)
_ = complex(1)
_ = dict((("a", 1),))
_ = float(123)
_ = list((1, 2, 3))
_ = str(123)
_ = tuple([1, 2, 3])
_ = int("0xFF")
