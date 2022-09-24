from textwrap import dedent

from refurb.loader import get_error_class, get_modules

from .error import ErrorCode


def explain(lookup: ErrorCode, paths: list[str] = []) -> str:
    for module in get_modules(paths):
        error = get_error_class(module)

        if error and ErrorCode.from_error(error) == lookup:
            return dedent(error.__doc__ or "").strip()

    return f'refurb: Error code "{lookup}" not found'
