# these should match

_ = isinstance(123, type(None))
_ = isinstance(123, (int, type(None)))
_ = isinstance(123, (type(None), int))
_ = isinstance(123, int | type(None))
_ = isinstance(123, int | float | type(None))
_ = isinstance(123, type(None) | int)
_ = isinstance(123, type(None) | int | float)


# these should not

_ = isinstance(123, int)
_ = isinstance(123, type(123))
_ = isinstance(123, (int, type(123)))
_ = isinstance(123, int | float)
