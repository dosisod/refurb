nums = [1, 2, 3]
t = (1, 2, 3)
barray = bytearray((0xFF,))

# these should match

_ = nums[:]
_ = t[:]
_ = barray[:]


class Wrapper:
    l: list[int]

w = Wrapper()
_ = w.l[:]


# these should not

_ = nums.copy()
_ = nums[1:]
_ = nums[:1]
_ = nums[::1]

nums[:] = [4, 5, 6]

class C:
    def __getitem__(self, key):
        return None

_ = C()[:,]

c = C()
_ = c[:]

s = "abc"
_ = s[:]

b = b"abc"
_ = b[:]


# special case that conflicts with FURB118, ignore
map(lambda x: x[:], [[]])  # noqa: FURB118
