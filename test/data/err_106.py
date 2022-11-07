# these will match

tabsize = 8

spaces_8 = "\thello world".replace("\t", " " * 8)
spaces_4 = "\thello world".replace("\t", "    ")
spaces_1 = "\thello world".replace("\t", " ")
spaces = "\thello world".replace("\t", " " * tabsize)
spaces = "\thello world".replace("\t", tabsize * " ")

bspaces_8 = b"\thello world".replace(b"\t", b" " * 8)
bspaces_4 = b"\thello world".replace(b"\t", b"    ")
bspaces_1 = b"\thello world".replace(b"\t", b" ")
bspaces = b"\thello world".replace(b"\t", b" " * tabsize)
bspaces = b"\thello world".replace(b"\t", tabsize * b" ")


# these will not

spaces = "\thello world".replace("\t", "x")
spaces = "\thello world".replace("x", " ")

bspaces = b"\thello world".replace(b"\t", b"x")
