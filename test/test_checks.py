from pathlib import Path

import pytest

from refurb.main import run_refurb


@pytest.mark.parametrize("test", Path("test/data").glob("*.py"))
def test_checks(test: Path) -> None:
    errors = run_refurb([str(test)])
    got = "\n".join([str(error) for error in errors])

    expected = test.with_suffix(".txt").read_text()[:-1]

    assert got == expected
