# these should match

_ = type(123) is type(None)
_ = type(123) == type(None)
_ = type(123) is not type(None)
_ = type(123) != type(None)


# these should not

_ = type(123) is type(456)
_ = type(123) is int
_ = int is type(None)
