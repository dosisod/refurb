import os
from pathlib import Path

file = Path("filename")
filename = "filename"
filename2 = b"filename"

# these should match

os.path.isabs("filename")
os.path.isdir("filename")
os.path.isfile("filename")
os.path.islink("filename")

os.path.isabs(file)
os.path.isdir(file)
os.path.isfile(file)
os.path.islink(file)

os.path.isabs(b"filename")
os.path.isdir(b"filename")
os.path.isfile(b"filename")
os.path.islink(b"filename")

os.path.isabs(filename)
os.path.isdir(filename)
os.path.isfile(filename)
os.path.islink(filename)

os.path.isabs(filename2)
os.path.isdir(filename2)
os.path.isfile(filename2)
os.path.islink(filename2)


# these should not

os.path.ismount("somefile")

file.is_absolute()
file.is_dir()
file.is_file()
file.is_symlink()
file.is_mount()

os.path.isdir(1)
os.path.isfile(1)
os.path.islink(1)
os.path.ismount(1)

fd = 1

os.path.isdir(fd)
os.path.isfile(fd)
os.path.islink(fd)
os.path.ismount(fd)
