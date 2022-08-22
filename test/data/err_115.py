# these should match

nums = [1, 2, 3]
authors = {"Dune": "Frank Herbert"}
primes = set((1, 2, 3, 5, 7))
data = (True, "something", 123)
name = "bob"
fruits = frozenset(("apple", "orange", "banana"))


_ = len(nums) == 0
_ = len(authors) == 0
_ = len(primes) == 0
_ = len(data) == 0
_ = len(name) == 0
_ = len(fruits) == 0


_ = len(nums) != 0
_ = len(nums) >= 1

_ = len([]) == 0
_ = len({}) == 0
_ = len(()) == 0
_ = len("") == 0
_ = len(set(())) == 0
_ = len(frozenset(())) == 0


# these should not

_ = len(nums) == 1
_ = len(nums) != 1


# We cannot verify all containers. For example, with this container, the length
# does not indicate whether it is truthy or not.
class Container:
    def __bool__(self) -> bool:
        return False

    def __len__(self) -> int:
        return 1337

container = Container()

_ = len(container) == 0
