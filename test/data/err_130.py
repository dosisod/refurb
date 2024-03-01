# these should match

d = {}

if "key" in d.keys():
    pass

if "key" not in d.keys():
    pass

x = "key"
if x in d.keys():
    pass

class C:
    d: dict[str, str]

if x in C().d.keys():
    pass


from collections.abc import Mapping

def mapping_check(m: Mapping[str, str]):
    if x in m.keys():
        pass


# these should not

if "key" in d:
    pass

if "key" in d.keys(1):  # type: ignore
    pass

if "key" not in d:
    pass


class NotADict:
    def keys(self) -> list[str]:
        return ["abc"]


not_a_dict = NotADict()

if "key" in not_a_dict.keys():
    pass
