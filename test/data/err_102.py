name = "bob"
last_name = b"smith"

# these should match
_ = name.startswith("a") or name.startswith("b")
_ = name.endswith("a") or name.endswith("b")
_ = last_name.startswith(b"a") or last_name.startswith(b"b")
_ = name.startswith("a") or name.startswith("b") or True

_ = not name.startswith("a") and not name.startswith("b")

class C:
    s: str

c = C()

_ = c.s.startswith("a") or c.s.startswith("b")

# TODO: disallow this because C() differs between branches
_ = C().s.startswith("a") or C().s.startswith("b")


# these should not match
_ = name.startswith("a") and name.startswith("b")

name_copy = name
_ = name.startswith("a") or name_copy.startswith("b")

_ = name.startswith() or name.startswith("x")  # type: ignore

_ = name.startswith("x") or name.startswith("y") and True

_ = not name.startswith("a") or not name.startswith("b")
_ = not name.startswith("a") and name.startswith("b")
_ = name.startswith("a") and not name.startswith("b")

_ = name.startswith("a", "b") or name.startswith("b")  # type: ignore
_ = name.startswith("a") or name.startswith()  # type: ignore
