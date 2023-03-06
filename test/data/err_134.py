import functools
from functools import cache, lru_cache

# these should match

@lru_cache(maxsize=None)
def f() -> None:
    pass

@functools.lru_cache(maxsize=None)
def f2() -> None:
    pass


# these should not

@lru_cache(maxsize=None, typed=True)
def f3() -> None:
    pass


@lru_cache(maxsize=100)
def f4() -> None:
    pass


@lru_cache
def f5() -> None:
    pass


@cache
def f6() -> None:
    pass
