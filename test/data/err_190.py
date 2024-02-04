# these will match

_ = lambda x: x.capitalize()
_ = lambda x: x.casefold()
_ = lambda x: x.isalnum()
_ = lambda x: x.isalpha()
_ = lambda x: x.isascii()
_ = lambda x: x.isdecimal()
_ = lambda x: x.isdigit()
_ = lambda x: x.isidentifier()
_ = lambda x: x.islower()
_ = lambda x: x.isnumeric()
_ = lambda x: x.isprintable()
_ = lambda x: x.isspace()
_ = lambda x: x.istitle()
_ = lambda x: x.isupper()
_ = lambda x: x.lower()
_ = lambda x: x.lstrip()
_ = lambda x: x.rsplit()
_ = lambda x: x.rstrip()
_ = lambda x: x.split()
_ = lambda x: x.splitlines()
_ = lambda x: x.strip()
_ = lambda x: x.swapcase()
_ = lambda x: x.title()
_ = lambda x: x.upper()


# these will not

y = ""

lambda *x: x.title()  # type: ignore
lambda x: y.title()
lambda: y.title()  # noqa: FURB111
lambda x, y: x.title()

lambda x: x + 1
lambda x: x.split("\n")
lambda x: x.strip().title()

# ignore if we deduce the type of x is non-str
map(lambda x: x.upper(), [1, 2, 3])  # type: ignore
