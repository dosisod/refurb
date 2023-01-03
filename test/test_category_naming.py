import re
from pathlib import Path

import refurb
from refurb.loader import get_error_class, get_modules


def test_check_categories_are_valid() -> None:
    # By "valid" I mean that they are well-defined (in the documentation), and
    # are sorted. Basically, parse the documentation file for the categories,
    # which includes a list of all categories, and make sure each check only
    # uses categories defined in that list. This prevents typos from causing
    # a check to have an incorrect category.

    category_docs = Path(refurb.__file__).parent.parent / "docs/categories.md"

    with category_docs.open() as f:
        categories = []

        for line in f:
            if name := re.search("## `([a-z-]+)`", line):
                categories.append(name.group(1))

    for module in get_modules([]):
        error = get_error_class(module)

        if not error:
            continue

        error_msg = f'{module.__file__}: categories missing for "{error.__name__}" class'
        assert error.categories or not error.enabled, error_msg

        error_msg = f'{module.__file__}: categories for "{error.__name__}" class are not sorted'

        assert sorted(error.categories) == error.categories, error_msg

        for category in error.categories:
            assert (
                category in categories
            ), f'{module.__file__}: category "{category}" is invalid'
