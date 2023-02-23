import re
from functools import cache
from pathlib import Path

import refurb
from refurb.error import Error
from refurb.loader import get_error_class, get_modules


def assert_category_exists(error: type[Error]) -> None:
    assert error.categories or not error.enabled, "categories field is missing"


def assert_categories_are_sorted(error: type[Error]) -> None:
    error_msg = "categories are not sorted"

    assert sorted(error.categories) == error.categories, error_msg


def assert_categories_are_valid(
    error: type[Error], categories: list[str]
) -> None:
    # By "valid" I mean that they are well-defined (in the documentation), and
    # are sorted. Basically, parse the documentation file for the categories,
    # which includes a list of all categories, and make sure each check only
    # uses categories defined in that list. This prevents typos from causing
    # a check to have an incorrect category.

    for category in error.categories:
        assert category in categories, f'category "{category}" is invalid'


def assert_name_field_in_valid_format(name: str) -> None:
    error_name_format = "^[a-z]+(-[a-z]+){1,}$"
    error_msg = f'name must be in format "{error_name_format}"'

    assert re.match(error_name_format, name), error_msg


def assert_name_is_unique(name: str, names: set[str]) -> None:
    assert name not in names, f'name "{name}" is already being used'

    names.add(name)


@cache
def get_categories_from_docs() -> list[str]:
    category_docs = Path(refurb.__file__).parent.parent / "docs/categories.md"

    with category_docs.open() as f:
        categories = []

        for line in f:
            if line.startswith("## "):
                categories.extend(
                    [cat.strip().strip("`") for cat in line[3:].split(", ")]
                )

        return categories


def test_checks_are_formatted_properly() -> None:
    error_names: set[str] = set()

    for module in get_modules([]):
        error = get_error_class(module)

        if not error:
            continue

        try:
            assert_category_exists(error)
            assert_categories_are_sorted(error)
            assert_categories_are_valid(error, get_categories_from_docs())

            assert error.name, "name field missing for class"

            assert_name_field_in_valid_format(error.name)
            assert_name_is_unique(error.name, error_names)

        except AssertionError as ex:
            raise ValueError(f"{module.__file__}: {ex}") from ex
