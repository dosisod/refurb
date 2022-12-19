b = True

# these should match

_ = b is True
_ = b is False
_ = b is not True
_ = b is not False
_ = True is b
_ = False is b

_ = b == True
_ = b == False
_ = b != True
_ = b != False
_ = True == b
_ = False == b


# these should not

class C:
    def __bool__(self) -> bool:
        return False

_ = C() is True

def f() -> bool | None:
    return None

x: bool | None = f()

_ = x is True

_ = b is b
_ = b is not b
