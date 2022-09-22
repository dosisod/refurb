from pathlib import Path

from refurb.main import run_refurb
from refurb.settings import Settings

TEST_DATA_PATH = Path("test/data")


def test_checks() -> None:
    errors = run_refurb(Settings(files=["test/"]))
    got = "\n".join([str(error) for error in errors])

    files = sorted(TEST_DATA_PATH.glob("*.txt"), key=lambda p: p.name)
    expected = "\n".join(file.read_text()[:-1] for file in files)

    assert got == expected


def test_fatal_mypy_error_is_bubbled_up() -> None:
    errors = run_refurb(Settings(files=["something"]))

    assert errors == [
        "refurb: can't read file 'something': No such file or directory"
    ]


def test_mypy_error_is_bubbled_up() -> None:
    errors = run_refurb(Settings(files=["some_file.py"]))

    assert errors == [
        "refurb: can't read file 'some_file.py': No such file or directory"
    ]


def test_ignore_check_is_respected() -> None:
    test_file = str(TEST_DATA_PATH / "err_100.py")

    errors = run_refurb(Settings(files=[test_file], ignore=set((100, 123))))

    assert len(errors) == 0


def test_system_exit_is_caught() -> None:
    test_pkg = "test/e2e/empty_package"

    errors = run_refurb(Settings(files=[test_pkg]))

    assert errors == [
        "refurb: There are no .py[i] files in directory 'test/e2e/empty_package'"
    ]
