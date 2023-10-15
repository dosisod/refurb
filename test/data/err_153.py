import os
import pathlib
from pathlib import Path
from os import path, curdir

# these should match

_ = Path(".")
_ = Path("")
_ = pathlib.Path(".")
_ = Path(os.curdir)
_ = Path(curdir)
_ = Path(os.path.curdir)
_ = Path(path.curdir)
_ = pathlib.Path(curdir)


# these should not

print(".")
Path("file.txt")
Path(".", "folder")
