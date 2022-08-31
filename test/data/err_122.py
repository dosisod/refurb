lines = ["line 1", "line 2", "line 3"]

# these will match

with open("file") as f:
    for line in lines:
        f.write(line)


with open("file", "wb") as f:
    for line in lines:
        f.write(line.encode())


with open("file") as f:
    for line in lines:
        f.write(line.upper())


# these will not

with open("x") as f:
    pass

    for line in lines:
        f.write(line)


with open("x") as f:
    for line in lines:
        pass

        f.write(line)
