from itertools import count

nums = (1, 2, 3)

# these should match

for index, _ in enumerate(nums):
    print(index)

for _, num in enumerate(nums):
    print(num)

_ = (index for index, _ in enumerate(nums))
_ = (num for _, num in enumerate(nums))

_ = {"key": index for index, _ in enumerate(nums)}
_ = {"key": num for _, num in enumerate(nums)}

_ = (1 for index, num in enumerate(nums))

_ = {"key": "value" for index, num in enumerate(nums)}

nums2 = [4, 5, 6]
nums3 = tuple((7, 8, 9))  # noqa: FURB123

_ = (index for index, _ in enumerate(nums3))


# these should not

for index, num in enumerate(nums):
    pass

# "count" is an infinite generator. In general, we only want to warn on
# sequence types because you can call len() on them without exhausting some
# iterator.
counter = count()
for index, _ in enumerate(counter):
    pass

_ = (num for index, num in enumerate(nums) if index)
