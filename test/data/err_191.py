b = True

# these should match

if b in {True, False}: pass
if b in {False, True}: pass
if b in [True, False]: pass  # noqa: FURB109
if b in [False, True]: pass  # noqa: FURB109
if b in (True, False): pass
if b in (False, True): pass

_ = [x for x in [] if b in (True, False)]  # noqa: FURB109
_ = {x for x in [] if b in (True, False)}  # noqa: FURB109
_ = (x for x in [] if b in (True, False))  # noqa: FURB109
_ = {k: v for k, v in {}.items() if b in (True, False)}

_ = 1 if b in (True, False) else 2

match b:
    case _ if b in (True, False):
        pass

while b in {True, False}:
    pass

assert b in {True, False}

if b not in {True, False}: pass

_ = b is True or b is False  # noqa: FURB149
_ = b is False or b is True  # noqa: FURB149

_ = b == True or b == False  # noqa: FURB149, FURB108
_ = b == False or b == True  # noqa: FURB149, FURB108


# these should not
if b in {True}: pass  # noqa: FURB171
if b in [True]: pass  # noqa: FURB109, FURB171
if b in (True,): pass  # noqa: FURB171

if b in {True, True}: pass

for x in [True, False]: pass  # noqa: FURB109

_ = [x for x in [True, False]]  # noqa: FURB109
_ = {x for x in [True, False]}  # noqa: FURB109
_ = (x for x in [True, False])  # noqa: FURB109

# TODO: suggest `isinstance(x, bool) or y`
if b in {True, False, 123}: pass
if b in {False, True, 123}: pass
if b in [True, False, 123]: pass  # noqa: FURB109
if b in [False, True, 123]: pass  # noqa: FURB109
if b in (True, False, 123): pass
if b in (False, True, 123): pass

if b == {True, False}: pass
if b == {False, True}: pass
if b == [True, False]: pass

b2 = False

_ = b is True or b is True  # noqa: FURB149
_ = b is False or b is False  # noqa: FURB149
_ = b is True or b is True  # noqa: FURB149
_ = b is True or b is b2  # noqa: FURB149
_ = b is b2 or b is True  # noqa: FURB149
_ = b is True or b2 is False  # noqa: FURB149
_ = b is not True or b is False  # noqa: FURB149
_ = b is False or b is not True  # noqa: FURB149

# TODO: support this later
_ = b is not True and b is not False  # noqa: FURB149
_ = b is not False and b is not True  # noqa: FURB149
