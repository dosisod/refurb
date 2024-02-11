nums = [1, 2, 3]

# these should match

del nums[:]

nums[:] = []

class C:
    nums: list[int]

del C().nums[:]

c = C()
del c.nums[:]

c.nums[:] = []


# these should not

names = {"key": "value"}

del names["key"]
del names[:]  # type: ignore

del nums[0]

x = 1
del x

del nums[1:]
del nums[:1]
del nums[::1]

nums[:] = [1, 2, 3]
nums[1:] = []
nums[:1] = []
nums[::1] = []
