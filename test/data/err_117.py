from pathlib import Path

# these will match

path = Path("filename")

with open(str(path)) as f:
    pass

with open(str(Path("filename"))) as f:
    pass

with open(Path("filename")) as f:
    pass

with open(path) as f:
    pass

with open(str(path), "rb") as f:
    pass

with open(path, "rb") as f:
    pass

f = open(str(path))

with open(path, encoding="utf-8") as f:
    pass

with open(path, "w", encoding="utf-8") as f:
    pass

with open(path, mode="rb") as f:
    pass

with open(path, "w", -1, "utf-8", "strict", "\n") as f:
    pass

mode = "rb"

with open(path, mode) as f:
    pass


# these will not

with Path("filename").open() as f:
    pass

with open("filename") as f:
    pass

# `Path.open()` has no `closefd` or `opener` parameters
with open(path, closefd=False) as f:
    pass

with open(path, "w", -1, None, None, None, False) as f:
    pass

with open(path, opener=lambda name, flags: 0) as f:
    pass

kwargs = {"closefd": False}

with open(path, **kwargs) as f:
    pass

args = ("w", -1, None, None, None, False)

with open(path, *args) as f:
    pass
