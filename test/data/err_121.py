num = num2 = 123

# these will match

_ = isinstance(num, float) or isinstance(num, int)
_ = isinstance(num, (float, str)) or isinstance(num, int)
_ = isinstance(num, (float, str)) or isinstance(num, int) or True


# these will not

_ = isinstance(num, float) or isinstance(num2, int)

def f(x, y):
    return True

_ = f(num, float) or f(num2, int)

_ = isinstance(num, (float, str)) or isinstance(num, int) and True
