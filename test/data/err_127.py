from contextlib import nullcontext, suppress

# these will match

def func():
    x = ""

    with nullcontext():
        x = "some value"


x = ""

with nullcontext():
    x = "some value"


# these will not

from contextlib import nullcontext
from typing import TYPE_CHECKING

if not TYPE_CHECKING:
    x = 1

    with nullcontext():
        y = 2


# see https://github.com/dosisod/refurb/issues/47
x = 1
with suppress(Exception):
    x = 2
