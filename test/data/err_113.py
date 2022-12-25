nums = []
nums2 = []

# these will match

nums.append(1)
nums.append(2)
pass


nums.append(1)
nums2.append(1)
nums.append(2)
nums.append(3)
pass


nums.append(1)
nums.append(2)
nums.append(3)


if True:
    nums.append(1)
    nums.append(2)


if True:
    nums.append(1)
    nums.append(2)
    pass


if True:
    nums.append(1)
    nums2.append(1)
    nums.append(2)
    nums.append(3)


# these will not

nums.append(1)
pass
nums.append(2)


if True:
    nums.append(1)
    pass
    nums.append(2)


nums.append(1)
pass


nums.append(1)
nums2.append(2)


nums.copy()
nums.copy()

class C:
    def append(self, x):
        pass

c = C()
c.append(1)
c.append(2)
