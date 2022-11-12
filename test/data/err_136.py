x = 1
y = 2

# these should match

_ = x if x < y else y
_ = x if x <= y else y
_ = x if x > y else y
_ = x if x >= y else y

_ = x if y < x else y
_ = x if y <= x else y
_ = x if y > x else y
_ = x if y >= x else y

# these should not

z = 3

_ = x if x < y else z
