x = 1
y = 2

# `pass` used as a filler to prevent this check from checking things it shouldnt
pass

# these will match

tmp = x
x = y
y = tmp

pass

filler = 1
tmp = x
x = y
y = tmp

pass

filler = 1
filler = 2
tmp = x
x = y
y = tmp

pass

tmp = x
x = y
y = tmp
tmp = x
x = y
y = tmp


# these will not

tmp = x
y = tmp
x = y

pass

tmp = x
x = y
tmp = 1
y = tmp

pass

tmp = x
x = y
pass
y = tmp

from typing import TYPE_CHECKING

# See https://github.com/dosisod/refurb/issues/23
if not TYPE_CHECKING:
    x = tmp
    x = tmp
    x = tmp
