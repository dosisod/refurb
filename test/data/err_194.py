# these should match

items = [1, 2, 3]

# basic pattern: next() with None default + is None check
x = next((i for i in items if i > 0), None)
if x is None:
    raise ValueError("no items")

# using == instead of is
y = next((i for i in items if i > 0), None)
if y == None:
    raise ValueError("no items")

# non-None sentinel
sentinel = object()
z = next((i for i in items if i > 0), sentinel)
if z is sentinel:
    raise ValueError("no items")

# reversed comparison
w = next((i for i in items if i > 0), None)
if None is w:
    raise ValueError("no items")


# these should not match

# no default argument
a = next(iter(items))

# default but no subsequent check
b = next(iter(items), None)
print(b)

# check but for different variable
c = next(iter(items), None)
if b is None:
    raise ValueError("wrong var")

# check but with else body
d = next(iter(items), None)
if d is None:
    raise ValueError("has else")
else:
    print(d)

# check but not a raise (just an assignment)
e = next(iter(items), None)
if e is None:
    e = 0

# different default value in check
f = next(iter(items), None)
if f is sentinel:
    raise ValueError("different sentinel")
