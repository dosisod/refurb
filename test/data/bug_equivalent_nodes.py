# These tests ensure that when comparing nodes to make sure that they are
# similar, extraneous info such as line numbers don't interfere. In short, if
# two nodes are semanticaly similar, but only differ in line number, they
# should still be considered equivalent.

# See issue #97

class Person:
    name: str
    age: int

    def __init__(self, name: str) -> None:
        self.name = name

bob = Person("bob")

# The following examples should all emit errors

_ = (
    bob.name
    if bob.name
    else "alice"
)


# These should not

_ = bob.age if bob.name else 123
