# these will match

x = list()
y = dict()
z = tuple()
i = int()
s = str()


# these will not

x = []
y = {}
z = ()
i = 0
s = ""

x = list((1, 2, 3))
y = dict((("a", 1), ("b", 2)))
i2 = int(123)
s2 = str(123)
