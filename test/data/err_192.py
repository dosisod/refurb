l = []

# these should match

_ = sorted(l)[0]
_ = sorted(l)[-1]
_ = sorted(l, reverse=True)[0]
_ = sorted(l, reverse=True)[-1]

_ = sorted(l, key=lambda x: x)[0]
_ = sorted(l, key=lambda x: x)[-1]
_ = sorted(l, key=lambda x: x, reverse=True)[0]
_ = sorted(l, key=lambda x: x, reverse=True)[-1]


# these should not

_ = sorted()[0]  # type: ignore
_ = sorted(l)[1]
_ = sorted(l)[-2]

b = True

_ = sorted(l, reverse=b)[0]
_ = sorted(l, invalid_kwarg=True)[0]  # type: ignore
