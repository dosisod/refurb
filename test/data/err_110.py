x = 123
y = 456

def f():
    return 1337


# these will match

z = x if x else y
z = True if True else y
z = (
    x
    if x
    else y
)

z = f() if f() else y


# these will not

z = x if y else y
z = y if x else y
