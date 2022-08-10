# these should match

x = "abc"

class C:
    y: str = "xyz"

c = C()


if x == "abc" or x == "def":
    pass

if c.y == "abc" or c.y == "def":
    pass

if x == "abc" or x == "def" or x == "ghi":
    pass

if (
    x == "abc"
    or x == "def"
):
    pass


# these should not

y = "abc"

if x == "abc" or y == "def":
    pass
