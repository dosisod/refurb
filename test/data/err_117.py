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


# these will not

with Path("filename").open() as f:
    pass

with open("filename") as f:
    pass
