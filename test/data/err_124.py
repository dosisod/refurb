x = y = z = 1

# these should match

_ = x == y and x == z
_ = x == y and y == z
_ = x == y and z == y
_ = x == y and x == z and True
_ = x == y and y == z and z == 1
_ = x == y and z == x


# these should not

_ = x == y and z == 1
_ = x == y or 1 == z
_ = x == y or 1 == z
_ = x == y or x <= z
