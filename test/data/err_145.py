nums = [1, 2, 3]
t = (1, 2, 3)
barray = bytearray((0xFF,))

# these should match

_ = nums[:]
_ = t[:]
_ = barray[:]


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
