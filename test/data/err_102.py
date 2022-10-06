name = "bob"
last_name = b"smith"

# these should match
_ = name.startswith("a") or name.startswith("b")
_ = name.endswith("a") or name.endswith("b")
_ = last_name.startswith(b"a") or last_name.startswith(b"b")
_ = name.startswith("a") or name.startswith("b") or True


# these should not match
_ = name.startswith("a") and name.startswith("b")

name_copy = name
_ = name.startswith("a") or name_copy.startswith("b")

_ = name.startswith() or name.startswith("x")

_ = name.startswith("x") or name.startswith("y") and True
