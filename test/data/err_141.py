import os
from os.path import exists
from pathlib import Path

# these should match

_ = os.path.exists("file")
_ = exists("file")

p = Path("file")
_ = os.path.exists(p)
_ = os.path.exists(Path("file"))


# these should not

_ = Path("file").exists()
