import re
from re import I

# these should match

_ = re.A
_ = re.I
_ = re.L
_ = re.M
_ = re.S
_ = re.T
_ = re.U
_ = re.X

_ = I


# these should not

_ = re.compile("^abc$")

class C:
    A: int = 123

_ = C.A
