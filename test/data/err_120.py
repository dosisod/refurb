def f(a: int = 1, b: int = 2) -> int:
    return a + b

def f2(a: int, b: int = 2, c: int = 3) -> int:
    return a + b + c

class C:
    def f(self, a: int = 1):
        return a

    @classmethod
    def f2(cls, a: int = 1):
        return a


# these should match

f(1)
f(1, 2)

f2(1, 2)
f2(1, 2, 3)
f(a=1)
f(b=2)

c = C()
c.f(1)
c.f2(1)
C.f2(1)
c.f(a=1)
c.f2(a=1)
C.f2(a=1)
# TODO: make this pass
# C().f1(1)

d = {}
d.get("unknown", None)

round(123, 0)
input("")
# TODO: make this pass
# int("123", 10)


# these should not

f()
f(2, 3)
f(b=1, a=2)

f2(1)
