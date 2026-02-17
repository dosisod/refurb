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

# short-circuit dependent: subscript/call in non-common operand (issue #350)
nums: list[int] = [1, 2, 3]
i = 0
_ = i == 0 or nums[i - 1] == 0
_ = i == 0 or len(nums) == 0
