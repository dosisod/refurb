# these should match

with open("file.txt") as f:
    x = f.read()

with open("file.txt", "rb") as f:
    x2 = f.read()

with open("file.txt", mode="rb") as f:
    x2 = f.read()

with open("file.txt", encoding="utf8") as f:
    x = f.read()

with open("file.txt", errors="ignore") as f:
    x = f.read()

with open("file.txt", errors="ignore", mode="rb") as f:
    x2 = f.read()

with open("file.txt", mode="r") as f:  # noqa: FURB120
    x = f.read()


# these should not

f2 = open("file2.txt")
with open("file.txt") as f:
    x = f2.read()

with open("file.txt") as f:
    # Path.read_text() does not support size, so ignore this
    x = f.read(100)

# enables line buffering, not supported in read_text()
with open("file.txt", buffering=1) as f:
    x = f.read()

# force CRLF, not supported in read_text()
with open("file.txt", newline="\r\n") as f:
    x = f.read()

# dont mistake "newline" for "mode"
with open("file.txt", newline="b") as f:
    x = f.read()
