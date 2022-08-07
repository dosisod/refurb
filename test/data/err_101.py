# these should match

with open("file.txt") as f:
    x = f.read()

with open("file.txt", "rb") as f:
    x2 = f.read()


# these should not

f2 = open("file2.txt")
with open("file.txt") as f:
    x = f2.read()
