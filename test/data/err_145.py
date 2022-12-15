# these should match

nums = [1, 2, 3]

_ = nums[:]
_ = [1, 2, 3][:]
_ = (1, 2, 3)[:]


# these should not

_ = nums.copy()
_ = nums[1:]
_ = nums[:1]
_ = nums[::1]

nums[:] = [4, 5, 6]

class C:
    def __getitem__(self, key):
        return None

C()[:,]
