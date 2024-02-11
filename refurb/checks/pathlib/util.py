from mypy.nodes import Expression

from refurb.checks.common import get_mypy_type, is_same_type


def is_pathlike(expr: Expression) -> bool:
    return is_same_type(get_mypy_type(expr), "pathlib.Path")
