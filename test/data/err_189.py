# these will match

class D(dict):
    pass

class L(list):
    pass

class S(str):
    pass


# these will not

class C:
    pass

class I(int):
    pass
