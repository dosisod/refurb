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

def func() -> bool:
    return True

_ = bool(func())

s = {1}
_ = set(s)
_ = set({1})

import os

_ = dict(os.environ)


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
_ = dict(**d)  # noqa: FURB173
_ = int(t)  # type: ignore
_ = int(*123)  # type: ignore
