from pathlib import Path

# test for additional instances where path objects should be checked

folder = Path("folder")

with open(folder / "file.txt") as f:
    pass

with open(folder / "another_folder" / "file.txt") as f:
    pass


class C:
    p: Path

with open(C().p) as f:
    pass

c = C()
with open(c.p) as f:
    pass


# these should not match

with open(folder + "file.txt") as f:  # type: ignore
    pass

with open("folder" / "file.txt") as f:  # type: ignore
    pass
