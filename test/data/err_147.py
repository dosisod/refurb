import os
from pathlib import Path

# these should match

os.path.join("a")
os.path.join("a", "b")
os.path.join("a", "b", "c")
os.path.join("a", "b", "c", "d")

os.path.join("some_path", "..")
os.path.join("some", "path", "..")
os.path.join("some", "other", "path", "..")
os.path.join("some", "path", "..", "..")
os.path.join("..", "some", "path")

os.path.join(b"a")
os.path.join(b"a", b"b")
os.path.join(b"a", b"b", b"c")
os.path.join(b"a", b"b", b"c", b"d")

os.path.join(b"some_path", b"..")
os.path.join(b"some", b"path", b"..")
os.path.join(b"some", b"other", b"path", b"..")
os.path.join(b"some", b"path", b"..", b"..")
os.path.join(b"..", b"some", b"path")


# these should not

os.path.join()  # type: ignore

Path("a")
Path("a", "b")
Path("a", "b", "c")
Path("a", "b", "c", "d")
