from pathlib import Path

import pytest

from refurb.main import Cli, run_refurb

TEST_DATA_PATH = Path("test/data")


@pytest.mark.parametrize("test", TEST_DATA_PATH.glob("*.py"))
def test_checks(test: Path) -> None:
    errors = run_refurb(Cli(files=[str(test)]))
    got = "\n".join([str(error) for error in errors])

    expected = test.with_suffix(".txt").read_text()[:-1]

    assert got == expected


def test_fatal_mypy_error_is_bubbled_up() -> None:
    errors = run_refurb(Cli(files=["something"]))

    assert errors == [
        "refurb: can't read file 'something': No such file or directory"
    ]


def test_mypy_error_is_bubbled_up() -> None:
    errors = run_refurb(Cli(files=["some_file.py"]))

    assert errors == [
        "refurb: can't read file 'some_file.py': No such file or directory"
    ]


def test_ignore_check_is_respected() -> None:
    test_file = str(TEST_DATA_PATH / "err_100.py")

    errors = run_refurb(Cli(files=[test_file], ignore=set((100,))))

    assert len(errors) == 0


def test_system_exit_is_caught() -> None:
    test_pkg = "test/e2e/empty_package"

    errors = run_refurb(Cli(files=[test_pkg]))

    assert errors == [
        "refurb: There are no .py[i] files in directory 'test/e2e/empty_package'"
    ]
