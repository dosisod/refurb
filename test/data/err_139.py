# these should match

"""
Hello world
""".lstrip()


"""\nHello world
""".lstrip()


"""
Hello world
""".lstrip("\n")


"""
Hello world
""".rstrip()


"""\nHello world
""".rstrip()


"""
Hello world
""".rstrip("\n")


"""
Hello world
""".strip()


"""
This is a test

""".strip()


"""\nHello world
""".strip()


"""
Hello world
""".strip("\n")


# these should not

"\n\n".lstrip()


"""

This is a test
""".lstrip()


"""
This is a test

""".rstrip()


"""
Testing 123
""".lstrip("x")


""" Testing 123
""".lstrip()


s = "Hello world"
s.lstrip()
