import shlex
from shlex import quote
from shlex import quote as shlex_quote

args = ["a", "b", "c d"]

# these should match

_ = " ".join(shlex.quote(arg) for arg in args)
_ = " ".join([shlex.quote(arg) for arg in args])
_ = " ".join(shlex.quote(arg) for arg in ("hello", "world"))
_ = " ".join(quote(arg) for arg in args)
_ = " ".join(shlex_quote(arg) for arg in args)

_ = " ".join(shlex.quote(arg + "") for arg in args)
_ = " ".join(shlex.quote(arg) for arg in args if arg)
_ = " ".join(shlex.quote(arg + "") for arg in args if arg)


# these should not

_ = " ".join(str(arg) for arg in args)  # noqa: FURB123
_ = " ".join(shlex.quote(arg, ...) for arg in args)  # type: ignore
_ = ";".join(shlex.quote(arg) for arg in args)
