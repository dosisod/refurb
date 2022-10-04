from pathlib import Path

from refurb.error import ErrorCode
from refurb.main import run_refurb
from refurb.settings import Settings, parse_command_line_args

TEST_DATA_PATH = Path("test/data")


def test_checks() -> None:
    errors = run_refurb(Settings(files=["test/data"]))
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

    errors = run_refurb(
        Settings(
            files=[test_file], ignore=set((ErrorCode(100), ErrorCode(123)))
        )
    )

    assert len(errors) == 0


def test_ignore_custom_check_is_respected() -> None:
    args = [
        "test/e2e/custom_check.py",
        "--load",
        "test.custom_checks.disallow_call",
    ]

    ignore_args = args + ["--ignore", "XYZ999"]

    errors_normal = run_refurb(parse_command_line_args(args))
    errors_while_ignoring = run_refurb(parse_command_line_args(ignore_args))

    assert errors_normal
    assert not errors_while_ignoring


def test_system_exit_is_caught() -> None:
    test_pkg = "test/e2e/empty_package"

    errors = run_refurb(Settings(files=[test_pkg]))

    assert errors == [
        "refurb: There are no .py[i] files in directory 'test/e2e/empty_package'"
    ]


DISABLED_CHECK = "test.custom_checks.disabled_check"


def test_disabled_check_is_not_ran_by_default() -> None:
    errors = run_refurb(
        Settings(files=["test/e2e/dummy.py"], load=[DISABLED_CHECK])
    )

    assert not errors


def test_disabled_check_ran_if_explicitly_enabled() -> None:
    errors = run_refurb(
        Settings(
            files=["test/e2e/dummy.py"],
            load=[DISABLED_CHECK],
            enable=set((ErrorCode(prefix="XYZ", id=999),)),
        )
    )

    expected = "test/e2e/dummy.py:1:1 [XYZ999]: This message is disabled by default"  # noqa: E501

    assert len(errors) == 1
    assert str(errors[0]) == expected
