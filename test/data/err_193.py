d: dict[str, int] = {}
key = "hello"

# these should match

d[key] = d.get(key, 0)
d["x"] = d.get("x", 10)

# these should not

# different keys
d["x"] = d.get("y", 0)

# different dicts
d2: dict[str, int] = {}
d["x"] = d2.get("x", 0)

# no default argument to .get()
d["x"] = d.get("x")

# not a .get() call
d["x"] = d.pop("x", 0)

# not a dict assignment
x = d.get("x", 0)
