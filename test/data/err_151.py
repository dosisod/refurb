from pathlib import Path

# these should match

open("file.txt", "w").close()
open("file.txt", "w+").close()
open("file.txt", mode="w+").close()

path = Path("file.txt")

open(path, "w").close()  # noqa: FURB117


# these should not

open("file.txt", "r").close()  # noqa: FURB120
open("file.txt", "w", encoding="utf8").close()
open("file.txt", encoding="w").close()
open("file.txt").close()
