from pathlib import Path

from refurb.error import Error, ErrorCategory, ErrorCode
from refurb.main import run_refurb
from refurb.settings import Settings, parse_command_line_args


def get_test_data_path() -> Path:
    data_path = Path(__file__).parent / "data"

    assert data_path.exists()
    assert data_path.is_dir()

    return data_path.relative_to(Path.cwd())


TEST_DATA_PATH = get_test_data_path()


def test_checks() -> None:
    run_checks_in_folder(TEST_DATA_PATH)


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
        Settings(files=[test_file], ignore={ErrorCode(100), ErrorCode(123)})
    )

    assert len(errors) == 0


def test_ignore_custom_check_is_respected() -> None:
    args = [
        "test/e2e/custom_check.py",
        "--load",
        "test.custom_checks.disallow_call",
    ]

    ignore_args = [*args, "--ignore", "XYZ100"]

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
            enable={ErrorCode(prefix="XYZ", id=101)},
        )
    )

    expected = "test/e2e/dummy.py:1:1 [XYZ101]: This message is disabled by default"  # noqa: E501

    assert len(errors) == 1
    assert str(errors[0]) == expected


def test_disabled_check_ran_if_enable_all_is_set() -> None:
    errors = run_refurb(
        Settings(
            files=["test/e2e/dummy.py"],
            load=[DISABLED_CHECK],
            enable_all=True,
        )
    )

    expected = "test/e2e/dummy.py:1:1 [XYZ101]: This message is disabled by default"  # noqa: E501

    assert len(errors) == 1
    assert str(errors[0]) == expected


def test_disable_all_will_only_load_explicitly_enabled_checks() -> None:
    errors = run_refurb(
        Settings(
            files=["test/data/"],
            disable_all=True,
            enable={ErrorCode(100)},
        )
    )

    assert all(
        isinstance(error, Error) and error.code == 100 for error in errors
    )


def test_disable_will_actually_disable_check_loading() -> None:
    errors = run_refurb(
        Settings(
            files=["test/data/err_123.py"],
            disable={ErrorCode(123)},
        )
    )

    assert not errors


def test_load_will_only_load_each_modules_once() -> None:
    errors_normal = run_refurb(
        Settings(
            files=["test/e2e/custom_check.py"],
            load=["test.custom_checks"],
        )
    )

    duplicated_load_errors = run_refurb(
        Settings(
            files=["test/e2e/custom_check.py"],
            load=["test.custom_checks", "test.custom_checks"],
        )
    )

    assert len(errors_normal) == len(duplicated_load_errors)


def test_load_builtin_checks_again_does_nothing() -> None:
    errors_normal = run_refurb(Settings(files=["test/data/err_100.py"]))

    duplicated_load_errors = run_refurb(
        Settings(
            files=["test/data/err_100.py"],
            load=["refurb"],
        )
    )

    assert len(errors_normal) == len(duplicated_load_errors)


def test_injection_of_settings_into_checks() -> None:
    errors = run_refurb(
        Settings(
            files=["test/e2e/dummy.py"],
            load=["test.custom_checks.settings"],
        )
    )

    msg = "test/e2e/dummy.py:1:1 [XYZ103]: Files being checked: ['test/e2e/dummy.py']"

    assert len(errors) == 1
    assert str(errors[0]) == msg


def test_explicitly_disabled_check_is_ignored_when_enable_all_is_set() -> None:
    errors = run_refurb(
        Settings(
            files=["test/data/err_123.py"],
            enable_all=True,
            disable={ErrorCode(123)},
        )
    )

    assert not errors


def test_explicitly_enabled_check_from_disabled_category_is_ran() -> None:
    errors = run_refurb(
        Settings(
            files=["test/data/err_123.py"],
            disable={ErrorCategory("readability")},
            enable={ErrorCode(123)},
        )
    )

    assert errors


def test_explicitly_enabled_category_still_runs() -> None:
    errors = run_refurb(
        Settings(
            files=["test/data/err_123.py"],
            disable_all=True,
            enable={ErrorCategory("readability")},
        )
    )

    assert errors


def test_error_not_ignored_if_path_doesnt_apply() -> None:
    errors = run_refurb(
        Settings(
            files=["test/data/err_123.py"],
            ignore={ErrorCode(123, path=Path("some_other_file.py"))},
        )
    )

    assert errors


def test_error_not_ignored_if_error_code_doesnt_apply() -> None:
    errors = run_refurb(
        Settings(
            files=["test/data/err_123.py"],
            ignore={ErrorCode(456, path=Path("test/data/err_123.py"))},
        )
    )

    assert errors


def test_error_ignored_if_path_applies() -> None:
    errors = run_refurb(
        Settings(
            files=["test/data/err_123.py"],
            ignore={ErrorCode(123, path=Path("test/data/err_123.py"))},
        )
    )

    assert not errors


def test_error_ignored_if_category_matches() -> None:
    error = ErrorCategory("readability", path=Path("test/data/err_123.py"))

    errors = run_refurb(
        Settings(files=["test/data/err_123.py"], ignore={error})
    )

    assert not errors


def test_checks_with_python_version_dependant_error_msgs() -> None:
    run_checks_in_folder(Path("test/data_3.9"), version=(3, 9))

    run_checks_in_folder(Path("test/data_3.10"), version=(3, 10))

    run_checks_in_folder(Path("test/data_3.11"), version=(3, 11))


def run_checks_in_folder(
    folder: Path, *, version: tuple[int, int] | None = None
) -> None:
    settings = Settings(files=[str(folder)], enable_all=True)

    if version:
        settings.python_version = version

    errors = run_refurb(settings)
    got = "\n".join([str(error) for error in errors])

    files = sorted(folder.glob("*.txt"), key=lambda p: p.name)
    expected = "\n".join(file.read_text()[:-1] for file in files)

    assert got == expected
