names = {"key": "value"}
nums = [1, 2, 3]

# these should match

del names["key"]
del nums[0]
del nums[:]


# these should not

x = 1
del x

del nums[1:2]
