nums = [1, 2, 3]

# these should match

# Here I am using `num + 1` because `num for num in nums` is basically the same
# as `nums` (and I plan to make a check for that in the future).

set(num + 1 for num in nums)
set([num + 1 for num in nums])
set({num + 1 for num in nums})

list(num + 1 for num in nums)
list([num + 1 for num in nums])

frozenset([num + 1 for num in nums])
frozenset({num + 1 for num in nums})

tuple([num + 1 for num in nums])

# these should not

_ = {num + 1 for num in nums}
_ = [num + 1 for num in nums]

list({num + 1 for num in nums})
tuple({num + 1 for num in nums})

set[int](num + 1 for num in nums)
list[int](num + 1 for num in nums)

frozenset(num + 1 for num in nums)
tuple(num + 1 for num in nums)
