# these should match

"""
Hello world
""".lstrip()


"""\nHello world
""".lstrip()


"""
Hello world
""".lstrip("\n")


# these should not

"\n\n".lstrip()


"""

This is a test
""".lstrip()


"""
Testing 123
""".lstrip("x")


""" Testing 123
""".lstrip()


s = "Hello world"
s.lstrip()
