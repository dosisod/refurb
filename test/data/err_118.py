# these will match

lambda x, y: x + y
lambda x, y: x - y
lambda x, y: x / y
lambda x, y: x // y
lambda x, y: x * y
lambda x, y: x @ y
lambda x, y: x ** y
lambda x, y: x is y
lambda x, y: x is not y
lambda x, y: x in y
lambda x, y: x & y
lambda x, y: x | y
lambda x, y: x ^ y
lambda x, y: x << y
lambda x, y: x >> y
lambda x, y: x % y
lambda x, y: x < y
lambda x, y: x <= y
lambda x, y: x == y
lambda x, y: x != y
lambda x, y: x >= y
lambda x, y: x > y

lambda x: ~ x
lambda x: - x
lambda x: not x
lambda x: + x

def f(x, y):
    return x + y

def f2(x):
    return - x


# these will not

lambda x, y: print(x + y)
lambda x, *y: x + y
lambda x, y: y + x
lambda x, y: 1 + 2
