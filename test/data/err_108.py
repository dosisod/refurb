x = y = "abc"

class C:
    y: str = "xyz"

c = C()


# these should match

_ = x == "abc" or x == "def"
_ = c.y == "abc" or c.y == "def"
_ = x == "abc" or x == "def" or x == "ghi"
_ = x == "abc" or x == "def" or y == "ghi"

_ = (
    x == "abc"
    or x == "def"
)

_ = x == "abc" or "def" == x
_ = "abc" == x or "def" == x
_ = "abc" == x or x == "def"

# these should not

_ = x == "abc" or y == "def"
_ = x == "abc" or x == "def" and y == "ghi"
