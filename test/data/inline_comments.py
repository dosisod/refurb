# these should be ignored

x = int(0)  # noqa: FURB123
x = int(0)  # noqa
x = int(0) # noqa
# line below contains trailing whitespace!
x = int(0) # noqa   
x = int(0)  # existing comment # noqa
x = int(0) # noqa: FURB123,RUF100
x = int(0) # noqa: FURB123, RUF100
x = int(0) # noqa:  FURB123, RUF100
x = int(0) # noqa: FURB123 RUF100
x = int(0) # noqa: FURB123 and RUF100
x = int(0), int(0)  # noqa: FURB123

# these should not

x = int(0)
x = int(0)  # some comment
x = int(0)  # noqa: FURB999
x = int(0)  # noqa: FURB1234
x = int(0)  # noqa: 123
x = str("# noqa: FURB123 ")
x = str('# noqa: FURB123 ')
