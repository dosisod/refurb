from dataclasses import dataclass

from refurb.error import Error
from refurb.main import Cli, main, run_refurb, sort_errors


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

    errors: list[Error | str] = [
        Error100(line=10, column=5, msg=""),
        Error101(line=1, column=5, msg=""),
        Error100(line=2, column=7, msg=""),
        Error100(line=1, column=10, msg=""),
        Error101(line=10, column=5, msg=""),
        "some other error",
    ]

    sorted_errors = list(sorted(errors, key=sort_errors))

    assert sorted_errors == [
        "some other error",
        Error101(line=1, column=5, msg=""),
        Error100(line=1, column=10, msg=""),
        Error100(line=2, column=7, msg=""),
        Error100(line=10, column=5, msg=""),
        Error101(line=10, column=5, msg=""),
    ]


def test_debug_flag():
    cli_options = Cli(files=["test/e2e/dummy.py"], debug=True)

    output = run_refurb(cli_options)

    print(output)

    assert output == [
        """\
MypyFile:1(
  test/e2e/dummy.py
  ExpressionStmt:1(
    StrExpr(\\u000aThis is a dummy file just to make sure that the refurb command is installed\\u000aand running correctly.\\u000a)))"""
    ]
