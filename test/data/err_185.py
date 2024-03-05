x = {}
y = set()

# these should match
_ = x.copy() | {}
_ = {} | x.copy()

_ = y.copy() | set()
_ = set() | y.copy()

_ = x.copy() | {} | x.copy()


class C:
    d: dict[str, str]


_ = C().d.copy() | {}

import os

_ = os.environ.copy() | {}


# these should not

class NotADict:
    def copy(self) -> dict:
        return {}

nd = NotADict()

_ = nd.copy() | {}
