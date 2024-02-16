# these should match

with open("file.txt") as f:
    for line in f.readlines():
        pass


with open("file.txt") as f:
    lines = [f"{line}!" for line in f.readlines()]


with open("file.txt") as f:
    lines = list(f"{line}!" for line in f.readlines())  # noqa: FURB137


with open("file.txt", "rb") as f:
    lines = list(f"{line}!" for line in f.readlines())  # noqa: FURB137


f = open("file.txt")
for line in f.readlines():
    pass


import io

class C:
    f: io.TextIOWrapper

for line in C().f.readlines():
    pass


# these will not

with open("file.txt") as f:
    for line in f.readlines(1):
        pass


with open("file.txt") as f:
    for line in f:
        pass


class Reader:
    @staticmethod
    def readlines() -> list[str]:
        return ["hello", "world"]

for line in Reader.readlines():
    pass


file = open("file.txt")
x = file.readlines()
