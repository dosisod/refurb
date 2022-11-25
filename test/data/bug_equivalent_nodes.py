# These tests ensure that when comparing nodes to make sure that they are
# similar, extraneous info such as line numbers don't interfere. In short, if
# two nodes are semanticaly similar, but only differ in line number, they
# should still be considered equivalent.

# See issue #97

class Person:
    name: str
    age: int

    def __init__(self, name: str) -> None:
        self.name = name

bob = Person("bob")

# The following examples should all emit errors

# member expr
_ = (
    bob.name
    if bob.name
    else "alice"
)

nums = [1, 2, 3]

# index expr
_ = (
    nums[0]
    if nums[0]
    else 123
)


def f(x: int) -> int:
    return x


# func call expr
_ = (
    f(1)
    if f(1)
    else 2
)

# list expr
_ = (
    [1, 2, 3]
    if [1, 2, 3]
    else []
)

# star "*" expr
_ = (
    [*nums, 4, 5, 6]
    if [*nums, 4, 5, 6]
    else []
)

# unary oper
_ = (
    not False
    if not False
    else False
)

# binary oper
_ = (
    1 + 2
    if 1 + 2
    else 3
)

# comparison expr
_ = (
    1 < 2
    if 1 < 2
    else 3
)

# slice expr
_ = (
    nums[1:]
    if nums[1:]
    else nums
)

# dict expr
_ = (
    {"k": "v"}
    if {"k": "v"}
    else {}
)

# tuple expr
_ = (
    (1, 2, 3)
    if (1, 2, 3)
    else ()
)

# set expr
_ = (
    {1, 2, 3}
    if {1, 2, 3}
    else set()
)


# These should not

_ = bob.age if bob.name else 123

_ = f(1) if f(2) else 2
_ = f(1) if f(x=1) else 2

_ = [1, 2, 3] if [1, 2, 3, 4] else []
_ = [1, 2, 3] if [1, 2, 4] else []

_ = [*nums, 1, 2, 3] if [*nums, 4, 5, 6] else []
_ = [*nums, 1, 2, 3] if [*nums, 1, 2, 3, 4] else []

nums2 = []

_ = [*nums, 1, 2, 3] if [*nums2, 1, 2, 3] else []

_ = - 1 if - 2 else 3
_ = - 1 if + 1 else 2

_ = 1 + 2 if 1 - 2 else 3
_ = 1 + 2 if 1 + 3 else 3
_ = 1 + 2 if 2 + 2 else 3

_ = 1 < 2 if 1 > 2 else 3
_ = 1 < 2 if 1 < 1 else 3
_ = 1 < 2 if 2 < 2 else 3
_ = 1 < 2 if 1 < 2 < 3 else 3

_ = nums[1:] if nums[2:] else nums
_ = nums[:1] if nums[:2] else nums
_ = nums[::1] if nums[::2] else nums

_ = {"k": "v"} if {"k": "not v"} else {}
_ = {"k": "v"} if {"not k": "v"} else {}
_ = {"k": "v"} if {"k": "v", "extra": "items"} else {}

_ = (1, 2, 3) if (1, 2, 3, 4) else ()
_ = (1, 2, 3) if (4, 5, 6) else ()

_ = {1, 2, 3} if {1, 2, 3, 4} else set()
_ = {1, 2, 3} if {4, 5, 6} else set()
