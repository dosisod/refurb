# these should match

_ = "abc".lstrip().rstrip()
_ = "abc".rstrip().lstrip()
_ = "abc".strip().rstrip()
_ = "abc".lstrip().strip()
_ = "abc".lstrip().lstrip()
_ = "abc".rstrip().rstrip()
_ = "abc".strip().strip()

_ = "abc".lstrip("x").rstrip("x")
_ = "abc".strip("x").rstrip("x")

_ = "abc".lstrip("x").lstrip("y")
_ = "abc".lstrip("x").lstrip("xy")
_ = "abc".lstrip("x").lstrip("x")
_ = "abc".strip("x").strip("y")

s = "hello world"
_ = s.lstrip().rstrip()


# these (maybe) should match
_ = "abc".lstrip("x").rstrip("xy")


# these should not

_ = "abc".lstrip().upper()
_ = "abc".upper().lstrip()
_ = "abc".lstrip("x").rstrip("y")
_ = "abc".strip("x").lstrip("y")
_ = "abc".strip("x").lstrip()
_ = "abc".strip().lstrip("x")

class C:
    def lstrip(self) -> str:
        return ""
    def rstrip(self) -> str:
        return ""

_ = C().lstrip().rstrip()
