# these should match

nums = [1, 2, 3]
authors = {"Dune": "Frank Herbert"}
primes = set((1, 2, 3, 5, 7))
data = (True, "something", 123)
name = "bob"
fruits = frozenset(("apple", "orange", "banana"))


if len(nums) == 0: ...
if len(authors) == 0: ...
if len(primes) == 0: ...
if len(data) == 0: ...
if len(name) == 0: ...
if len(fruits) == 0: ...

if len(nums) <= 0: ...
if len(nums) > 0: ...
if len(nums) != 0: ...
if len(nums) >= 1: ...

if len([]) == 0: ...
if len({}) == 0: ...
if len(()) == 0: ...
if len("") == 0: ...
if len(set(())) == 0: ...
if len(frozenset(())) == 0: ...

if True and len(nums) == 0: ...

match 1:
    case 1 if len(nums) == 0:
        pass

_ = [x for x in () if len(nums) == 0]
_ = (x for x in () if len(nums) == 0)
_ = {"k": v for v in () if len(nums) == 0}

_ = 1 if len(nums) == 0 else 2

while len(nums) == 0:
    pass

assert len(nums) == 0


# len(x)

if len(nums): ...

match 1:
    case 1 if len(nums):
        pass

_ = [x for x in () if len(nums)]
_ = (x for x in () if len(nums))
_ = {"k": v for v in () if len(nums)}

_ = 1 if len(nums) else 2

while len(nums):
    pass

assert len(nums)

assert nums == []
assert nums != []

assert authors == {}
assert authors != {}

assert len(nums) and True
assert len(nums) or False


# these should not

if len(nums) == 1: ...
if len(nums) != 1: ...

x = len(nums) == 0


# We cannot verify all containers. For example, with this container, the length
# does not indicate whether it is truthy or not.
class Container:
    def __bool__(self) -> bool:
        return False

    def __len__(self) -> int:
        return 1337

container = Container()

if len(container) == 0: ...

if print(len(nums) == 0): ...
if (lambda: len(nums) == 0)(): ...

assert nums == [1, 2, 3]
assert authors == {"author": "book"}
assert nums <= []

assert len(nums) % 2
