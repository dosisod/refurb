# these will match

for x in [1, 2, 3]:
    pass

[x for x in [1, 2, 3]]

(x for x in [1, 2, 3])

[
    (x + y) for x in [1, 2, 3]
    for y in [4, 5, 6]
]

if 1 in [1, 2, 3]:
    pass

if 1 not in [1, 2, 3]:
    pass


# these will not

nums = [1, 2, 3]
for x in nums:
    pass

for x in list((1, 2, 3)):
    pass

[x for x in list((1, 2, 3))]

if 1 in list((1, 2, 3)):
    pass
