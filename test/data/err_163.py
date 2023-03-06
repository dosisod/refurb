import math
from math import e, log

# these should match

_ = math.log(64, 2)
_ = math.log(64, 2.0)
_ = math.log(100, 10)
_ = math.log(100, 10.0)
_ = math.log(100, math.e)
_ = math.log(100, e)
_ = math.log(1 + 2, 2)
_ = log(100, 10)


# these should not

_ = math.log(10, 3)
_ = math.log(64, 1 + 1)

two = 2
_ = math.log(10, two)
