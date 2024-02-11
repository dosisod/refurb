s = set()

# these should match

if "x" in s:
    s.remove("x")


class Wrapper:
    s: set[int]

w = Wrapper()

if 0 in w.s:
    w.s.remove(0)

# these should not

if "x" in s:
    s.remove("y")

s.discard("x")

s2 = set()

if "x" in s:
    s2.remove("x")

if "x" in s:
    s.remove("x")
    print("removed item")

class Container:
    def remove(self, item) -> None:
        return

    def __contains__(self, other) -> bool:
        return True

c = Container()

if "x" in c:
    c.remove("x")

if "x" in s:
    s.remove("x")
else:
    pass
