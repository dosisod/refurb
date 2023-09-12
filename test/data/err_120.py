from typing import overload


def f(a: int = 1, b: int = 2) -> int:
    return a + b

def f2(a: int, b: int = 2, c: int = 3) -> int:
    return a + b + c

class C:
    x: int

    def __init__(self, x: int = 1) -> None:
        self.x = x

    def f(self, a: int = 1):
        return a

    @classmethod
    def f2(cls, a: int = 1):
        return a

    @staticmethod
    def f3(x: int = 1):
        pass

    @staticmethod
    def f4():
        pass

@overload
def over() -> None: ...

@overload
def over(x: int = 1) -> None: ...

def over(x: int = 2, y: int = 3) -> None:
    pass

class C2:
    @overload
    @staticmethod
    def over() -> None: ...

    @overload
    @staticmethod
    def over(x: int = 1) -> None: ...

    @staticmethod
    def over(x: int = 2, y: int = 3) -> None:
        pass


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
C().f(1)  # noqa: FURB165
C().f2(1)  # noqa: FURB165
C(x=1)
C.f3(1)

d = {}
d.get("unknown", None)

round(123, 0)
input("")
int("123", 10)

def args(*args, x: int = 1):
    pass

args(x=1)
args(None, x=1)
args(None, None, x=1)

over(1)
over(2)

C2.over(1)
C2.over(2)

f(0, 2)
f(1, b=3)


# these should not

f()
f(2, 3)
f(b=1, a=2)

f2(1)
int("123")

def kw(**kwargs):
    pass

kw(x=1)

C.f4()

args(1)
args(None, 1)
args(None, None, 1)
args(x=2)
args(None, x=2)
args(None, None, x=2)
