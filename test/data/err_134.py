from functools import cache, lru_cache

# these should match

@lru_cache(maxsize=None)
def f() -> None:
    pass


# these should not

@lru_cache(maxsize=None, typed=True)
def f2() -> None:
    pass


@lru_cache(maxsize=100)
def f3() -> None:
    pass


@lru_cache
def f4() -> None:
    pass


@cache
def f5() -> None:
    pass
