# these will match

x = list()
y = dict()
z = tuple()
i = int()
s = str()
f = float()
c = complex()
b = bool()
by = bytes()


# these will not

x = []
y = {}
z = ()
i = 0
s = ""

x = list((1, 2, 3))
y = dict((("a", 1), ("b", 2)))
i2 = int("0xFF")
s2 = str(123)
