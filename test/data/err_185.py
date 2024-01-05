x = {}
y = set()

# these should match
_ = x.copy() | {}
_ = {} | x.copy()

_ = y.copy() | set()
_ = set() | y.copy()

_ = x.copy() | {} | x.copy()



class C:
    def copy(self) -> dict:
        return {}

c = C()


# these should not
_ = c.copy() | {}
