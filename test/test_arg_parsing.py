import pytest

from refurb.error import ErrorCode
from refurb.settings import Settings, merge_settings
from refurb.settings import parse_command_line_args as parse_args
from refurb.settings import parse_config_file, parse_error_id


def test_parse_explain():
    assert parse_args(["--explain", "123"]) == Settings(explain=ErrorCode(123))


def test_parse_explain_missing_option() -> None:
    msg = 'refurb: missing argument after "--explain"'

    with pytest.raises(ValueError, match=msg):
        parse_args(["--explain"])


def test_parse_explain_furb_prefix() -> None:
    assert parse_args(["--explain", "FURB123"]) == Settings(
        explain=ErrorCode(123)
    )


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


def test_parse_help_args() -> None:
    assert parse_args([]) == Settings(help=True)
    assert parse_args(["--help"]) == Settings(help=True)
    assert parse_args(["-h"]) == Settings(help=True)


def test_parse_version_args() -> None:
    assert parse_args(["--version"]) == Settings(version=True)
    assert parse_args(["-v"]) == Settings(version=True)


def test_parse_ignore() -> None:
    got = parse_args(["--ignore", "FURB123", "--ignore", "321"])
    expected = Settings(ignore=set((ErrorCode(123), ErrorCode(321))))

    assert got == expected


def test_parse_ignore_check_missing_arg() -> None:
    with pytest.raises(
        ValueError, match='refurb: missing argument after "--ignore"'
    ):
        parse_args(["--ignore"])


def test_parse_enable() -> None:
    got = parse_args(["--enable", "FURB123", "--enable", "321"])
    expected = Settings(enable=set((ErrorCode(123), ErrorCode(321))))

    assert got == expected


def test_parse_enable_check_missing_arg() -> None:
    with pytest.raises(
        ValueError, match='refurb: missing argument after "--enable"'
    ):
        parse_args(["--enable"])


def test_debug_parsing() -> None:
    assert parse_args(["--debug", "file"]) == Settings(
        files=["file"], debug=True
    )


def test_quiet_flag_parsing() -> None:
    assert parse_args(["--quiet", "file"]) == Settings(
        files=["file"], quiet=True
    )


def test_generate_subcommand() -> None:
    assert parse_args(["gen"]) == Settings(generate=True)


def test_load_flag() -> None:
    assert parse_args(["--load", "some_module"]) == Settings(
        load=["some_module"]
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
enable = ["FURB111", "FURB222"]
"""

    config = parse_config_file(contents)

    assert config == Settings(
        load=["some", "folders"],
        ignore=set((ErrorCode(100), ErrorCode(101))),
        enable=set((ErrorCode(111), ErrorCode(222))),
    )


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
        ignore=set((ErrorCode(100), ErrorCode(101))),
    )


def test_command_line_args_override_config_file() -> None:
    contents = """\
[tool.refurb]
load = ["some", "folders"]
ignore = [100, "FURB101"]
enable = ["FURB111", "FURB222"]
"""

    command_line_args = parse_args(
        ["--load", "x", "--ignore", "123", "--enable", "FURB200"]
    )
    config_file = parse_config_file(contents)

    config = merge_settings(command_line_args, config_file)

    assert config == Settings(
        load=["x"],
        ignore=set((ErrorCode(123),)),
        enable=set((ErrorCode(200),)),
    )


def test_config_missing_ignore_option_is_allowed() -> None:
    contents = """\
[tool.refurb]
load = ["x"]
"""

    assert parse_config_file(contents) == Settings(load=["x"])


def test_config_missing_load_option_is_allowed() -> None:
    contents = """\
[tool.refurb]
ignore = [123]
"""

    assert parse_config_file(contents) == Settings(
        ignore=set((ErrorCode(123),))
    )


def test_parse_error_codes() -> None:
    tests = {
        "FURB123": ErrorCode(123),
        "123": ErrorCode(123),
        "ABC100": ErrorCode(prefix="ABC", id=100),
        "ABCDE100": ValueError,
        "ABC1234": ValueError,
        "AB123": ValueError,
        "invalid": ValueError,
        "12": ValueError,
        "-123": ValueError,
    }

    for input, output in tests.items():
        if output == ValueError:
            with pytest.raises(ValueError):
                parse_error_id(input)

        else:
            assert parse_error_id(input) == output
