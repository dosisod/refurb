# these should be ignored

x = int(0)  # noqa: FURB123
x = int(0)  # noqa
x = int(0) # noqa
x = int(0)  # existing comment # noqa

# these should not

x = int(0)
x = int(0)  # some comment
x = int(0)  # noqa: FURB999
x = int(0)  # noqa: 123
