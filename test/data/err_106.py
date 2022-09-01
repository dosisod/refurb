# these will match

tabsize = 8

spaces_8 = "hello\tworld".replace("\t", " " * 8)
spaces_4 = "hello\tworld".replace("\t", "    ")
spaces_1 = "hello\tworld".replace("\t", " ")
spaces = "hello\tworld".replace("\t", " " * tabsize)

bspaces_8 = b"hello\tworld".replace(b"\t", b" " * 8)
bspaces_4 = b"hello\tworld".replace(b"\t", b"    ")
bspaces_1 = b"hello\tworld".replace(b"\t", b" ")
bspaces = b"hello\tworld".replace(b"\t", b" " * tabsize)


# these will not

spaces = "hello\tworld".replace("\t", "x")
spaces = "hello\tworld".replace("x", " ")

bspaces = b"hello\tworld".replace(b"\t", b"x")
