# These are a variety of checks to ensure Refurb is able to deduce types from
# complex expressions.

_ = bool([True][0])


async def async_wrapper():
    import asyncio

    async def return_bool() -> bool:
        return True

    task = asyncio.create_task(return_bool())

    _ = bool(await return_bool())
    _ = bool(await task)


lambda_return_bool = lambda: True
_ = bool(lambda_return_bool())
_ = bool((lambda: True)())  # TODO: error message should include parens around lambda

bool_value = True

_ = bool(not bool_value)
_ = bool(not False)

_ = int(-1)
_ = int(+1)
_ = int(~1)

_ = bool(walrus := True)

from typing import cast

_ = bool(cast(bool, 123))


DictAlias = dict[str, str]

# Must use function here so that `d` uses the `DictAlias` type alias. If an intermediate
# object is used the alias will "resolve" and won't trigger the type alias check.
def dict_alias_wrapper(d: DictAlias) -> None:
    _ = dict(d)


# These types are not able to be deduced (yet)
_ = int(1 or 2)
