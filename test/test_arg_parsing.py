import pytest

from refurb.main import Cli, parse_args


def test_parse_explain():
    assert parse_args(["--explain", "123"]) == Cli(explain=123)


@pytest.mark.parametrize("args", (["--explain"], ["--explain", "123", "456"]))
def test_parse_explain_missing_option(args: list[str]) -> None:
    with pytest.raises(ValueError, match="usage: refurb --explain ID"):
        parse_args(args)

    with pytest.raises(ValueError, match="usage: refurb --explain ID"):
        parse_args(args)


def test_parse_explain_furb_prefix() -> None:
    assert parse_args(["--explain", "FURB123"]) == Cli(explain=123)


def test_require_numbers_as_explain_id() -> None:
    with pytest.raises(
        ValueError, match='refurb: "abc" must be in form FURB123 or 123'
    ):
        parse_args(["--explain", "abc"])


def test_parse_files() -> None:
    assert parse_args(["a", "b", "c"]) == Cli(files=["a", "b", "c"])


def test_check_for_unsupported_flags() -> None:
    with pytest.raises(ValueError, match='refurb: unsupported option "-x"'):
        parse_args(["-x"])


def test_no_args_is_check() -> None:
    with pytest.raises(ValueError, match="refurb: no arguments passed"):
        parse_args([])
