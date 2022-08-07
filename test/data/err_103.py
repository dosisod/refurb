# these will match

with open("filename", "w") as f:
    f.write("hello world")

with open("filename", "wb") as f:
    f.write(b"hello world")


# these will not

with open("filename") as f:
    f.write("hello world")

f2 = open("filename2")
with open("filename") as f:
    f2.write("hello world")
