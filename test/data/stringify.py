# test double star in dict expr
_ = dict({**{}})

# test different slice exprs
_ = list([""[0]])
_ = list([""[1:]])
_ = list([""[1:2]])
_ = list([""[1:2:-1]])
_ = list([""[::-1]])
