from dataclasses import dataclass
from pathlib import Path

from refurb.error import Error
from refurb.main import format_as_github_annotation


def test_string_error_messages_are_translated_as_is() -> None:
    msg = format_as_github_annotation("testing")

    assert msg == "::error title=Refurb Error::testing"


def test_error_is_converted_correctly() -> None:
    @dataclass
    class CustomError(Error):
        prefix = "ABC"
        code = 123
        msg: str = "This is a test"

    absolute_path = Path("filename.py").resolve()

    error = CustomError(line=1, column=2, filename=str(absolute_path))

    # column is 3 due to mypy node columns starting at 0
    expected = "::error line=1,col=3,title=Refurb ABC123,file=filename.py::This is a test"

    assert format_as_github_annotation(error) == expected
