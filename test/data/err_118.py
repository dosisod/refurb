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
lambda x, y: y in x
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

lambda x: ~x
lambda x: -x
lambda x: not x
lambda x: +x

def f(x, y):
    return x + y

def f2(x):
    return - x

lambda x: x[0]

lambda x: (x[0], x[1], x[2])
lambda x: (x[1:], x[2])


# these will not

lambda x, y: print(x + y)
lambda x, *y: x + y
lambda x, y: y + x
lambda x, y: 1 + 2
lambda x: (1, x[1], x[2])
lambda x: (x.y, x[1], x[2])
lambda x, y: (x[0], y[0])
lambda x, y: (x[0], y[0])
lambda x: ()
lambda x: (*x[0], x[1])
