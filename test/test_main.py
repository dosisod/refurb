from dataclasses import dataclass

from refurb.error import Error
from refurb.main import main, sort_errors


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

    errors = [
        Error100(line=10, column=5, msg=""),
        Error101(line=1, column=5, msg=""),
        Error100(line=2, column=7, msg=""),
        Error100(line=1, column=10, msg=""),
        Error101(line=10, column=5, msg=""),
    ]

    sorted_errors = list(sorted(errors, key=sort_errors))

    assert sorted_errors == [
        Error101(line=1, column=5, msg=""),
        Error100(line=1, column=10, msg=""),
        Error100(line=2, column=7, msg=""),
        Error100(line=10, column=5, msg=""),
        Error101(line=10, column=5, msg=""),
    ]
