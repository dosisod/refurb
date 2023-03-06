import os
from os import remove, unlink
from pathlib import Path

# these should match

os.remove("file")
os.unlink("file")

file = Path("file")
os.remove(file)
os.unlink(file)

remove("file")
unlink("file")

# these should not

os.remove("file", dir_fd=1)
os.unlink("file", dir_fd=1)

Path("file").unlink()
