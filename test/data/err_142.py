# these should match

s = set()

for x in (1, 2, 3):
    s.add(x)

for x in (1, 2, 3):
    s.discard(x)

for x in (1, 2, 3):
    s.add(x + 1)


class C:
    s: set[int]

c = C()
for x in (1, 2, 3):
    c.s.add(x)


# these should not

s.update(x for x in (1, 2, 3))

num = 123

for x in (1, 2, 3):
    s.add(num)

for x in (1, 2, 3):
    s.add(x)
else:
    pass

async def f(y):
    async for x in y:
        s.add(x)


def g():
    for x in (set(),):
        x.add(x)

# TODO: support unpacked tuples here
for x, y in ((1, 2), (3, 4)):
    s.add((x, y))
