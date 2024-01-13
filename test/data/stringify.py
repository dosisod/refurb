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
