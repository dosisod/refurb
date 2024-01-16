# these should match

_ = 1 in (1,)
_ = 1 in [1]  # noqa: FURB109
_ = 1 in {1}
_ = 1 not in (1,)
_ = 1 not in [1]  # noqa: FURB109
_ = 1 not in {1}  # noqa: FURB109


# these should not

_ = 1 in (1, 2)
_ = 1 in [1, 2]  # noqa: FURB109
