# `if` blocks are used to separate test cases
x = 1
y = 2

# these will match

if True:
    tmp = x
    x = y
    y = tmp

if True:
    filler = 1
    tmp = x
    x = y
    y = tmp

if True:
    filler = 1
    filler = 2
    tmp = x
    x = y
    y = tmp

if True:
    tmp = x
    x = y
    y = tmp
    tmp = x
    x = y
    y = tmp


# these will not

if True:
    tmp = x
    y = tmp
    x = y

if True:
    tmp = x
    x = y
    tmp = 1
    y = tmp

if True:
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
