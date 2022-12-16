x = y = z = 1

# these should match

_ = x == y and x == z
_ = x == y and y == z
_ = x == y and z == y
_ = x == y and x == z and True
_ = x == y and y == z and z == 1
_ = x == y and z == x

_ = x is None and y is None
_ = x is None and None is y
_ = None is x and y is None
_ = x is None and y is None and True


# these should not

_ = x == y and z == 1
_ = x == y or 1 == z
_ = x == y or 1 == z
_ = x == y or x <= z

_ = x is None and y is 1
_ = x is None or y is None
