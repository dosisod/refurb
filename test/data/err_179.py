from itertools import chain
import itertools


rows = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

def f():
    return rows

# these should match

def flatten_via_generator(rows):
    return (col for row in rows for col in row)

def flatten_via_list_comp(rows):
    return [col for row in rows for col in row]

def flatten_via_set_comp(rows):
    return {col for row in rows for col in row}

def flatten_with_function_source():
    return (col for row in f() for col in row)

def flatten_via_sum(rows):
    return sum(rows, [])

def flatten_via_chain_splat(rows):
    return chain(*rows)

def flatten_via_chain_splat_2(rows):
    return itertools.chain(*rows)


# these should not

def flatten_via_generator_modified(rows):
    return (col + 1 for row in rows for col in row)

def flatten_via_generator_modified_2(rows):
    return (col for [row] in rows for col in row)

def flatten_via_generator_modified_3(rows):
    return (col for row in rows for [col] in row)

def flatten_via_generator_with_if(rows):
    return (col for row in rows for col in row if col)

def flatten_via_generator_with_if_2(rows):
    return (col for row in rows if row for col in row)

def flatten_via_dict_comp(rows):
    return {col: "" for row in rows for col in row}

async def flatten_async_generator(rows):
    return (col async for row in rows for col in row)

async def flatten_async_generator_2(rows):
    return (col for row in rows async for col in row)

async def flatten_async_generator_3(rows):
    return (col async for row in rows async for col in row)

def flatten_via_sum_with_default(rows):
    return sum(rows, [1])

def flatten_via_chain_without_splat(rows):
    return chain(rows)

def flatten_via_chain_from_iterable(rows):
    return chain.from_iterable(rows)
