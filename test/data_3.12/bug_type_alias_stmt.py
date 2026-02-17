# PEP 695 type alias statements should not crash refurb.
# See https://github.com/dosisod/refurb/issues/359

type OptStr = str | None

type Point = tuple[float, float]

x: list[int] = list(range(10))
y = x[:]
