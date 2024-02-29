# test double star in dict expr
_ = dict({**{}})

# test different slice exprs
_ = list([""[0]])
_ = list([""[1:]])
_ = list([""[1:2]])
_ = list([""[1:2:-1]])
_ = list([""[::-1]])

# test slice exprs
lambda x: x[1:]
lambda x: x[1:2]
lambda x: x[1:2:3]
lambda x: x[1::3]
lambda x: x[:2:3]
lambda x: x[::3]
lambda x: x[:2:]
lambda x: x[::]
lambda x: x[:]

# test fstring formatting
_ = str(f"{123}")  # noqa: FURB183
_ = str(f"{123:x}")
_ = str(f"x{123}y")
_ = str(f"x{123}y{456}z")
_ = str(f"{'abc'}")  # noqa: FURB183
_ = str(f"{123}\n")

# wont trigger fstring stringify code
_ = str("".join([""]))
_ = str("".join(["", 1]))  # type: ignore
