import os
from dataclasses import dataclass
from locale import LC_ALL, setlocale
from unittest.mock import patch

import pytest

from refurb.error import Error
from refurb.main import main, run_refurb, sort_errors
from refurb.settings import Settings


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

    sorted_errors = list(sorted(errors, key=sort_errors))

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
            main(args)  # type: ignore

            p.assert_called_once()
            assert "usage" in p.call_args[0][0]


def test_version_flag_calls_version_func():
    for args in (["--version"], ["-v"]):
        with patch("refurb.main.version") as p:
            main(args)

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


@pytest.mark.skipif(not os.getenv("CI"), reason="Locale installation required")
def test_utf8_is_used_to_load_files_when_error_occurs():  # type: ignore
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
