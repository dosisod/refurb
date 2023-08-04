# See https://github.com/dosisod/refurb/issues/18 and https://github.com/dosisod/refurb/issues/53

# This is a regression test to make sure this code doesn't cause an error

x = "abc"
print(x)  # see below
x = 1
y = str(x)


# The print(x) line is needed because of the overly-strict "allow_redefinition"
# option in Mypy, which requires that a variable be read before it allows the
# creation of a new instance. The following code should fail, until Mypy fixes
# it (if they do).

x2 = "abc"
x2 = 1
y2 = str(x2)
