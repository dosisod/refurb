# these should match

s = set()

for x in (1, 2, 3):
    s.add(x)

for x in (1, 2, 3):
    s.discard(x)

for x in (1, 2, 3):
    s.add(x + 1)


# these should not

s.update(x for x in (1, 2, 3))

num = 123

for x in (1, 2, 3):
    s.add(num)

for x in (set(),):
    x.add(x)

# TODO: support unpacked tuples here
for x, y in ((1, 2), (3, 4)):
    s.add((x, y))
