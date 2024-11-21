import json
import os
from dataclasses import dataclass
from functools import partial
from importlib import metadata
from locale import LC_ALL, setlocale
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import patch

import pytest

from refurb.error import Error, ErrorCategory, ErrorClassifier, ErrorCode
from refurb.main import is_ignored_via_amend, main, run_refurb, sort_errors
from refurb.settings import Settings, load_settings, parse_command_line_args


def test_invalid_args_returns_error_code():
    assert main(["--invalid"]) == 1


def test_explain_returns_success_code():
    assert main(["--explain", "100"]) == 0


def test_run_refurb_no_errors_returns_success_code():
    assert main(["test/e2e/dummy.py"]) == 0


def test_run_refurb_with_errors_returns_error_code():
    assert main(["non_existent_file.py"]) == 1


def test_errors_are_sorted():
    @dataclass
    class Error100(Error):
        code = 100

    @dataclass
    class Error101(Error):
        code = 101

    @dataclass
    class CustomError100(Error):
        prefix = "ABC"
        code = 100

    errors: list[Error | str] = [
        Error100(filename="0_first", line=10, column=5, msg=""),
        Error101(filename="1_last", line=1, column=5, msg=""),
        Error100(filename="0_first", line=2, column=7, msg=""),
        Error100(filename="1_last", line=1, column=10, msg=""),
        Error101(filename="0_first", line=10, column=5, msg=""),
        Error100(filename="1_last", line=10, column=5, msg=""),
        Error101(filename="0_first", line=1, column=5, msg=""),
        Error100(filename="1_last", line=2, column=7, msg=""),
        Error100(filename="0_first", line=1, column=10, msg=""),
        Error101(filename="1_last", line=10, column=5, msg=""),
        CustomError100(filename="1_last", line=10, column=5, msg=""),
        "some other error",
    ]

    settings = Settings(sort_by="filename")
    sorted_errors = sorted(errors, key=lambda e: sort_errors(e, settings))

    assert sorted_errors == [
        "some other error",
        Error101(filename="0_first", line=1, column=5, msg=""),
        Error100(filename="0_first", line=1, column=10, msg=""),
        Error100(filename="0_first", line=2, column=7, msg=""),
        Error100(filename="0_first", line=10, column=5, msg=""),
        Error101(filename="0_first", line=10, column=5, msg=""),
        Error101(filename="1_last", line=1, column=5, msg=""),
        Error100(filename="1_last", line=1, column=10, msg=""),
        Error100(filename="1_last", line=2, column=7, msg=""),
        CustomError100(filename="1_last", line=10, column=5, msg=""),
        Error100(filename="1_last", line=10, column=5, msg=""),
        Error101(filename="1_last", line=10, column=5, msg=""),
    ]

    settings.sort_by = "error"
    sorted_errors = sorted(errors, key=partial(sort_errors, settings=settings))

    assert sorted_errors == [
        "some other error",
        CustomError100(filename="1_last", line=10, column=5, msg=""),
        Error100(filename="0_first", line=1, column=10, msg=""),
        Error100(filename="0_first", line=2, column=7, msg=""),
        Error100(filename="0_first", line=10, column=5, msg=""),
        Error100(filename="1_last", line=1, column=10, msg=""),
        Error100(filename="1_last", line=2, column=7, msg=""),
        Error100(filename="1_last", line=10, column=5, msg=""),
        Error101(filename="0_first", line=1, column=5, msg=""),
        Error101(filename="0_first", line=10, column=5, msg=""),
        Error101(filename="1_last", line=1, column=5, msg=""),
        Error101(filename="1_last", line=10, column=5, msg=""),
    ]


def test_debug_flag():
    settings = Settings(files=["test/e2e/dummy.py"], debug=True)

    output = run_refurb(settings)

    assert output == [
        """\
MypyFile:1(
  test/e2e/dummy.py
  ExpressionStmt:1(
    StrExpr(\\u000aThis is a dummy file just to make sure that the refurb command is installed\\u000aand running correctly.\\u000a)))"""
    ]


def test_generate_subcommand():
    with patch("refurb.main.generate") as p:
        main(["gen"])

        p.assert_called_once()


def test_help_flag_calls_print():
    for args in (["--help"], ["-h"], []):
        with patch("builtins.print") as p:
            main(args)

            p.assert_called_once()
            assert "usage" in p.call_args[0][0]


def test_version_flag_calls_version_func():
    with patch("refurb.main.version") as p:
        main(["--version"])

        p.assert_called_once()


def test_explain_flag_mentioned_if_error_exists():
    with patch("builtins.print") as p:
        main(["test/data/err_100.py"])

        p.assert_called_once()
        assert "Run `refurb --explain ERR`" in p.call_args[0][0]


def test_explain_flag_not_mentioned_when_quiet_flag_is_enabled():
    with patch("builtins.print") as p:
        main(["test/data/err_100.py", "--quiet"])

        p.assert_called_once()
        assert "Run `refurb --explain ERR`" not in p.call_args[0][0]


def test_no_blank_line_printed_if_there_are_no_errors():
    with patch("builtins.print") as p:
        main(["test/e2e/dummy.py"])

        assert p.call_count == 0


def test_invalid_checks_returns_nice_message() -> None:
    with patch("builtins.print") as p:
        args = [
            "test/e2e/dummy.py",
            "--load",
            "test.invalid_checks.invalid_check",
        ]

        main(args)

        expected = 'test/invalid_checks/invalid_check.py:13: "int" is not a valid Mypy node type'

        assert expected in str(p.call_args[0][0])


@pytest.mark.skipif(not os.getenv("CI"), reason="Locale installation required")
def test_utf8_is_used_to_load_files_when_error_occurs() -> None:
    """
    See issue https://github.com/dosisod/refurb/issues/37. This check will
    set the zh_CN.GBK locale, run a particular file, and if all goes well,
    no exception will be thrown. This test is only ran when the CI environment
    variable is set, which is set by GitHub Actions.
    """

    setlocale(LC_ALL, "zh_CN.GBK")

    try:
        main(["test/e2e/gbk.py"])

    except UnicodeDecodeError:
        setlocale(LC_ALL, "")

        raise

    setlocale(LC_ALL, "")


def test_load_custom_config_file():
    args = [
        "test/data/err_101.py",
        "--quiet",
        "--config-file",
        "test/config/config.toml",
    ]

    errors = run_refurb(load_settings(args))

    assert not errors


def test_amended_ignores_are_relative_to_config_file():
    os.chdir("test")

    args = [
        "data/err_123.py",
        "--config-file",
        "config/amend_config.toml",
    ]

    errors = run_refurb(load_settings(args))

    os.chdir("..")

    assert not errors


def test_raise_error_if_config_file_is_invalid():
    tests = {
        ".": "is a directory",
        "file_not_found": "was not found",
    }

    for config_file, expected in tests.items():
        with pytest.raises(ValueError, match=expected):
            load_settings(["--config-file", config_file])


def test_mypy_args_are_forwarded() -> None:
    errors = run_refurb(Settings(mypy_args=["--version"]))

    assert len(errors) == 1
    assert isinstance(errors[0], str)
    assert errors[0].startswith(f"mypy {metadata.version('mypy')}")


def test_stub_files_dont_hide_errors() -> None:
    errors = run_refurb(parse_command_line_args(["test/e2e/stub_pkg"]))

    assert len(errors) == 1
    assert "FURB123" in str(errors[0])


def test_verbose_flag_prints_all_enabled_checks() -> None:
    with patch("builtins.print") as p:
        main(["test/data/err_100.py", "--verbose", "--enable-all"])

    stdout = "\n".join(args[0][0] for args in p.call_args_list)

    # Current number of checks at time of writing. This number doesn't need to
    # be kept updated, it is only set to a known value to verify that it is
    # doing what it should.
    current_check_count = 76

    for error_id in range(100, 100 + current_check_count):
        assert f"FURB{error_id}" in stdout


def test_verbose_flag_prints_message_when_all_checks_disabled() -> None:
    with patch("builtins.print") as p:
        main(["test/data/err_100.py", "--verbose", "--disable-all"])

    stdout = "\n".join(args[0][0] for args in p.call_args_list)

    assert "FURB100" not in stdout
    assert "No checks enabled" in stdout


def test_timing_stats_outputs_stats_file() -> None:
    with NamedTemporaryFile(mode="r", encoding="utf8") as tmp:
        main(["test/e2e/dummy.py", "--timing-stats", tmp.name])

        stats_file = Path(tmp.name)

        assert stats_file.exists()

        data = json.loads(stats_file.read_text())

        match data:
            case {
                "mypy_total_time_spent_in_ms": int(_),
                "mypy_time_spent_parsing_modules_in_ms": dict(mypy_timing),
                "refurb_time_spent_checking_file_in_ms": dict(refurb_timing),
            }:
                msg = "All values must be ints"

                assert all(isinstance(v, int) for v in mypy_timing.values()), msg

                assert all(isinstance(v, int) for v in refurb_timing.values()), msg

                return

        pytest.fail("Data is not in proper format")


def test_color_is_enabled_by_default():
    with patch("builtins.print") as p:
        main(["test/data/err_123.py"])

        p.assert_called_once()
        assert "\x1b" in p.call_args[0][0]


def test_no_color_printed_when_disabled():
    with patch("builtins.print") as p:
        main(["test/data/err_123.py", "--no-color"])

        p.assert_called_once()
        assert "\x1b" not in p.call_args[0][0]


def test_error_github_actions_formatting():
    with patch("builtins.print") as p:
        main(["test/data/err_123.py", "--format", "github"])

        p.assert_called_once()
        assert "::error" in p.call_args[0][0]


@pytest.mark.parametrize(
    ("ignore_set", "expected"),
    [
        (set(), False),
        ({ErrorCode(123, path=Path())}, True),
        ({ErrorCode(321, path=Path())}, False),
        ({ErrorCode(123, path=Path("test/inner"))}, False),
        ({ErrorCategory("pythonic", path=Path())}, True),
        ({ErrorCategory("pythonic", path=Path("test/inner"))}, False),
        ({ErrorCategory("other", path=Path())}, False),
    ],
)
def test_is_ignored_via_amend(ignore_set: set[ErrorClassifier], expected: bool) -> None:
    class Error123(Error):
        code = 123
        categories = ("pythonic", "builtin")
        name = "test-error"

    settings = Settings(ignore=ignore_set)
    error = Error123(line=1, column=1, msg="Error msg.", filename="test/error.py")
    assert is_ignored_via_amend(error, settings) is expected
