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

sets: dict[int, set[str]] = {1: set(), 2: set()}
to_update = [1, 2]

for a in to_update:
    sets[a].add("abc")

# TODO: support unpacked tuples here
for x, y in ((1, 2), (3, 4)):
    s.add((x, y))


def get_set(x: int) -> set[int]:
    return set()


# set target is a function call referencing the loop variable (should not warn)
for x in (1, 2, 3):
    get_set(x).add(x)

# set target is a function call NOT referencing the loop variable (should warn)
for x in (1, 2, 3):
    get_set(0).add(x)

# set target uses a constant index — same set every iteration (should warn)
for a in to_update:
    sets[1].add("abc")
