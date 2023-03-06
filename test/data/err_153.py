import pathlib
from pathlib import Path

# these should match

_ = Path(".")
_ = Path("")
_ = pathlib.Path(".")


# these should not

print(".")
Path("file.txt")
Path(".", "folder")
