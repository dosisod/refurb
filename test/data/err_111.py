# these will match

def f(x, y):
    pass

mod = object


lambda: print()
lambda x: bool(x)
lambda x, y: f(x, y)

lambda: []
lambda: {}
lambda: ()

lambda x: mod.cast(x)

_ = lambda: 0
_ = lambda: 0.0
_ = lambda: 0j
_ = lambda: False
_ = lambda: ""
_ = lambda: b""


# these will not

lambda: f(True, False)
lambda x: f(x, True)
lambda x, y: f(y, x)
lambda x: bool(x + 1)
lambda x: x + 1
lambda x: print(*x)
lambda x: print(**x)
lambda: True

lambda: [1, 2, 3]
lambda: {"k": "v"}
lambda: (1, 2, 3)

lambda: None
lambda: 1
lambda: 1.2
lambda: True
lambda: "abc"
lambda: b"abc"
lambda: 1j
lambda: set()  # noqa: FURB111
lambda: {"x"}

import datetime

_ = lambda: datetime.datetime.now().today()
