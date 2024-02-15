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


class Wrapper:
    l: list[int]

if True:
    w = Wrapper()
    w.l.append(1)
    w.l.append(2)


# these will not

nums.append(1)
pass
nums.append(2)


if True:
    nums.append(1)
    pass
    nums.append(2)


if True:
    nums.append()  # type: ignore
    nums.append()  # type: ignore


if True:
    nums.append(1, 2)  # type: ignore
    nums.append(3, 4)  # type: ignore


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
