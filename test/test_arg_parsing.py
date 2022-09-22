import pytest

from refurb.settings import Settings, merge_settings
from refurb.settings import parse_command_line_args as parse_args
from refurb.settings import parse_config_file


def test_parse_explain():
    assert parse_args(["--explain", "123"]) == Settings(explain=123)


@pytest.mark.parametrize("args", (["--explain"], ["--explain", "123", "456"]))
def test_parse_explain_missing_option(args: list[str]) -> None:
    with pytest.raises(ValueError, match="usage: refurb --explain ID"):
        parse_args(args)

    with pytest.raises(ValueError, match="usage: refurb --explain ID"):
        parse_args(args)


def test_parse_explain_furb_prefix() -> None:
    assert parse_args(["--explain", "FURB123"]) == Settings(explain=123)


def test_require_numbers_as_explain_id() -> None:
    with pytest.raises(
        ValueError, match='refurb: "abc" must be in form FURB123 or 123'
    ):
        parse_args(["--explain", "abc"])


def test_parse_files() -> None:
    assert parse_args(["a", "b", "c"]) == Settings(files=["a", "b", "c"])


def test_check_for_unsupported_flags() -> None:
    with pytest.raises(ValueError, match='refurb: unsupported option "-x"'):
        parse_args(["-x"])


def test_no_args_is_check() -> None:
    with pytest.raises(ValueError, match="refurb: no arguments passed"):
        parse_args([])


def test_parse_ignore() -> None:
    got = parse_args(["--ignore", "FURB123", "--ignore", "321"])
    expected = Settings(files=[], ignore=set((123, 321)))

    assert got == expected


def test_parse_ignore_check_missing_arg() -> None:
    with pytest.raises(
        ValueError, match='refurb: missing argument after "--ignore"'
    ):
        parse_args(["--ignore"])


def test_debug_parsing() -> None:
    assert parse_args(["--debug", "file"]) == Settings(
        files=["file"], debug=True
    )


def test_generate_subcommand() -> None:
    assert parse_args(["gen"]) == Settings(generate=True)


def test_load_flag() -> None:
    assert parse_args(["--load", "some_module"]) == Settings(
        files=[], load=["some_module"]
    )


def test_parse_load_flag_missing_arg() -> None:
    with pytest.raises(
        ValueError, match='refurb: missing argument after "--load"'
    ):
        parse_args(["--load"])


def test_parse_config_file() -> None:
    contents = """\
[tool.refurb]
load = ["some", "folders"]
ignore = [100, "FURB101"]
"""

    config = parse_config_file(contents)

    assert config == Settings(load=["some", "folders"], ignore=set((100, 101)))


def test_merge_command_line_args_and_config_file() -> None:
    contents = """\
[tool.refurb]
load = ["some", "folders"]
ignore = [100, "FURB101"]
"""

    command_line_args = parse_args(["some_file.py"])
    config_file = parse_config_file(contents)

    config = merge_settings(command_line_args, config_file)

    assert config == Settings(
        files=["some_file.py"],
        load=["some", "folders"],
        ignore=set((100, 101)),
    )


def test_command_line_args_override_config_file() -> None:
    contents = """\
[tool.refurb]
load = ["some", "folders"]
ignore = [100, "FURB101"]
"""

    command_line_args = parse_args(["--load", "x", "--ignore", "123"])
    config_file = parse_config_file(contents)

    config = merge_settings(command_line_args, config_file)

    assert config == Settings(files=[], load=["x"], ignore=set((123,)))
