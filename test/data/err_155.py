import os
from os.path import getatime, getctime, getmtime, getsize
from pathlib import Path

# these should match

os.path.getatime("filename")
os.path.getatime(b"filename")
os.path.getatime(Path("filename"))
getatime("filename")

os.path.getmtime("filename")
os.path.getmtime(b"filename")
os.path.getmtime(Path("filename"))
getmtime("filename")

os.path.getctime("filename")
os.path.getctime(b"filename")
os.path.getctime(Path("filename"))
getctime("filename")

os.path.getsize("filename")
os.path.getsize(b"filename")
os.path.getsize(Path("filename"))
os.path.getsize(__file__)
getsize("filename")

# this should not match
os.path.getsize(1)
