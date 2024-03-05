x = {"a": 1}
y = {"b": 2}
z = {"c": 3}

# these should match

_ = {**x, **y}
_ = {**x, "b": 2}
_ = {**x, "b": 2, "c": 3}
_ = {"a": 1, **x}
_ = {"a": 1, "b": 2, **x}
_ = {"a": 1, **x, **y}
_ = {**x, **y, "c": 3}
_ = {**x, **y, **z}
_ = {**x, **y, **z, **x}
_ = {**x, **y, **z, **x, **x}
_ = {**x, **y, **z, **x, "a": 1}

from collections import ChainMap, Counter, OrderedDict, defaultdict, UserDict

chainmap = ChainMap()
_ = {"k": "v", **chainmap}

counter = Counter()
_ = {"k": "v", **counter}

ordereddict = OrderedDict()
_ = {"k": "v", **ordereddict}

dd = defaultdict()
_ = {"k": "v", **dd}

userdict = UserDict()
_ = {"k": "v", **userdict}


_ = dict(**x)
_ = dict(x, **y)
_ = dict(**x, **y)
_ = dict(x, a=1)
_ = dict(**x, a=1, b=2)
_ = dict(**x, **y, a=1, b=2)
_ = dict(**x, **{})

class Wrapper:
    d: dict

_ = {**Wrapper().d, **x}

from collections.abc import Mapping, MutableMapping


def mapping_test(m: Mapping[str, str]):
    _ = dict(**m)

def mutable_mapping_test(m: MutableMapping[str, str]):
    _ = dict(**m)


import os

_ = dict(**os.environ)


# these should not

_ = {}
_ = {**x}
_ = {**x, "a": 1, **y}
_ = {"a": 1}
_ = {"a": 1, "b": 2}
_ = {"a": 1, **x, "b": 2}


class C:
    from typing import Any

    def keys(self):
        return []

    def __getitem__(self, key: str) -> Any:
        pass


c = C()

_ = {"k": "v", **c}

_ = dict(x)  # noqa: FURB123
_ = dict(*({},))
_ = dict()  # noqa: FURB112
_ = dict(a=1, b=2)

_ = dict(**x, **[])  # type: ignore
