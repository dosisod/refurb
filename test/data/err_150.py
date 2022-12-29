import os
from pathlib import Path

path = Path("folder")

# these should match

os.mkdir("folder")
os.mkdir(b"folder")
os.mkdir(path)
os.mkdir("folder", mode=0o644)
os.mkdir("folder", 0o644)

os.makedirs("folder")
os.makedirs(b"folder")
os.makedirs(path)
os.makedirs("folder", mode=0o644)
os.makedirs("folder", 0o644)
os.makedirs("folder", exist_ok=True)
os.makedirs("folder", exist_ok=False)
os.makedirs("folder", exist_ok=False, mode=0o644)


# these should not

os.mkdir("folder", dir_fd=1)
os.mkdir()  # type: ignore
os.makedirs()  # type: ignore
