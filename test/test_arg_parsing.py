import os
from pathlib import Path
from unittest.mock import patch

import pytest

from refurb.error import ErrorCategory, ErrorCode
from refurb.settings import Settings
from refurb.settings import parse_command_line_args as parse_args
from refurb.settings import parse_config_file, parse_error_id


def test_parse_explain():
    assert parse_args(["--explain", "123"]) == Settings(explain=ErrorCode(123))


def test_parse_explain_missing_option() -> None:
    msg = 'refurb: missing argument after "--explain"'

    with pytest.raises(ValueError, match=msg):
        parse_args(["--explain"])


def test_parse_explain_furb_prefix() -> None:
    assert parse_args(["--explain", "FURB123"]) == Settings(explain=ErrorCode(123))


def test_require_numbers_as_explain_id() -> None:
    with pytest.raises(ValueError, match='refurb: "abc" must be in form FURB123 or 123'):
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


def test_parse_ignore() -> None:
    got = parse_args(["--ignore", "FURB123", "--ignore", "321"])
    expected = Settings(ignore={ErrorCode(123), ErrorCode(321)})

    assert got == expected


def test_parse_ignore_category() -> None:
    got = parse_args(["--ignore", "#category"])
    expected = Settings(ignore={ErrorCategory("category")})

    assert got == expected


def test_parse_ignore_check_missing_arg() -> None:
    with pytest.raises(ValueError, match='refurb: missing argument after "--ignore"'):
        parse_args(["--ignore"])


def test_parse_enable() -> None:
    got = parse_args(["--enable", "FURB123", "--enable", "321"])
    expected = Settings(enable={ErrorCode(123), ErrorCode(321)})

    assert got == expected


def test_parse_enable_category() -> None:
    got = parse_args(["--enable", "#category"])
    expected = Settings(enable={ErrorCategory("category")})

    assert got == expected


def test_parse_enable_check_missing_arg() -> None:
    with pytest.raises(ValueError, match='refurb: missing argument after "--enable"'):
        parse_args(["--enable"])


def test_debug_parsing() -> None:
    assert parse_args(["--debug", "file"]) == Settings(files=["file"], debug=True)


def test_quiet_flag_parsing() -> None:
    assert parse_args(["--quiet", "file"]) == Settings(files=["file"], quiet=True)


def test_generate_subcommand() -> None:
    assert parse_args(["gen"]) == Settings(generate=True)


def test_load_flag() -> None:
    assert parse_args(["--load", "some_module"]) == Settings(load=["some_module"])


def test_parse_load_flag_missing_arg() -> None:
    with pytest.raises(ValueError, match='refurb: missing argument after "--load"'):
        parse_args(["--load"])


def test_parse_config_file_flag_missing_arg() -> None:
    with pytest.raises(ValueError, match='refurb: missing argument after "--config-file"'):
        parse_args(["--config-file"])


def test_config_file_flag() -> None:
    assert parse_args(["--config-file", "some_file"]) == Settings(
        config_file="some_file",
    )


def test_parse_config_file() -> None:
    contents = """\
[tool.refurb]
load = ["some", "folders"]
ignore = [100, "FURB101"]
enable = ["FURB111", "FURB222"]
format = "github"
sort_by = "error"
color = false
"""

    config = parse_config_file(contents)

    assert config == Settings(
        load=["some", "folders"],
        ignore={ErrorCode(100), ErrorCode(101)},
        enable={ErrorCode(111), ErrorCode(222)},
        format="github",
        sort_by="error",
        color=False,
    )


def test_merge_command_line_args_and_config_file() -> None:
    contents = """\
[tool.refurb]
load = ["some", "folders"]
ignore = [100, "FURB101"]
"""

    command_line_args = parse_args(["some_file.py"])
    config_file = parse_config_file(contents)

    merged = Settings.merge(config_file, command_line_args)

    assert merged == Settings(
        files=["some_file.py"],
        load=["some", "folders"],
        ignore={ErrorCode(100), ErrorCode(101)},
    )


def test_command_line_args_merge_config_file() -> None:
    contents = """\
[tool.refurb]
load = ["some", "folders"]
ignore = [100, "FURB101"]
enable = ["FURB111", "FURB222"]
quiet = true
format = "github"
sort_by = "error"
python_version = "3.7"
mypy_args = ["some", "args"]
"""

    command_line_args = parse_args(["--load", "x", "--ignore", "123", "--enable", "FURB200"])
    config_file = parse_config_file(contents)

    merged = Settings.merge(config_file, command_line_args)

    assert merged == Settings(
        load=["some", "folders", "x"],
        ignore={ErrorCode(100), ErrorCode(101), ErrorCode(123)},
        enable={ErrorCode(111), ErrorCode(222), ErrorCode(200)},
        quiet=True,
        format="github",
        sort_by="error",
        python_version=(3, 7),
        mypy_args=["some", "args"],
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

    assert parse_config_file(contents) == Settings(ignore={ErrorCode(123)})


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
        if output is ValueError:
            msg = "must be in form FURB123 or 123"

            with pytest.raises(ValueError, match=msg):
                parse_error_id(input)

        else:
            assert parse_error_id(input) == output


def test_disable_error() -> None:
    settings = parse_args(["--disable", "FURB100"])

    assert settings == Settings(disable={ErrorCode(100)})


def test_disable_error_category() -> None:
    settings = parse_args(["--disable", "#category"])

    assert settings == Settings(disable={ErrorCategory("category")})


def test_disable_existing_enabled_error() -> None:
    settings = parse_args(["--enable", "FURB100", "--disable", "FURB100"])

    assert settings == Settings(disable={ErrorCode(100)})


def test_enable_existing_disabled_error() -> None:
    settings = parse_args(["--disable", "FURB100", "--enable", "FURB100"])

    assert settings == Settings(enable={ErrorCode(100)})


def test_parse_disable_check_missing_arg() -> None:
    with pytest.raises(ValueError, match='refurb: missing argument after "--disable"'):
        parse_args(["--disable"])


def test_disable_in_config_file() -> None:
    contents = """\
[tool.refurb]
disable = ["FURB111", "FURB222"]
"""

    config_file = parse_config_file(contents)

    assert config_file == Settings(disable={ErrorCode(111), ErrorCode(222)})


def test_disable_overrides_enable_in_config_file() -> None:
    contents = """\
[tool.refurb]
enable = ["FURB111", "FURB222"]
disable = ["FURB111", "FURB333", "FURB444"]
"""

    config_file = parse_config_file(contents)

    assert config_file == Settings(
        enable={ErrorCode(222)},
        disable={ErrorCode(111), ErrorCode(333), ErrorCode(444)},
    )


def test_disable_cli_arg_overrides_config_file() -> None:
    contents = """\
[tool.refurb]
enable = ["FURB111", "FURB222", "FURB333"]
disable = ["FURB111", "FURB444"]
"""

    config_file = parse_config_file(contents)

    command_line_args = parse_args(["--disable", "FURB333"])

    merged = Settings.merge(config_file, command_line_args)

    assert merged == Settings(
        enable={ErrorCode(222)},
        disable={ErrorCode(111), ErrorCode(333), ErrorCode(444)},
    )


def test_disable_all_flag_parsing() -> None:
    assert parse_args(["--disable-all", "file"]) == Settings(files=["file"], disable_all=True)


def test_disable_all_flag_disables_existing_enables() -> None:
    settings = parse_args(["--enable", "FURB123", "--disable-all", "--enable", "FURB456"])

    assert settings == Settings(disable_all=True, enable={ErrorCode(456)})


def test_disable_all_in_config_file() -> None:
    contents = """\
[tool.refurb]
disable_all = true
enable = ["FURB123"]
"""

    config_file = parse_config_file(contents)

    assert config_file == Settings(
        disable_all=True,
        enable={ErrorCode(123)},
    )


def test_disable_all_command_line_override() -> None:
    contents = """\
[tool.refurb]
disable_all = false
enable = ["FURB123"]
"""

    config_file = parse_config_file(contents)

    command_line_args = parse_args(["--disable-all", "--enable", "FURB456"])

    merged = Settings.merge(config_file, command_line_args)

    assert merged == Settings(
        disable_all=True,
        enable={ErrorCode(456)},
    )


def test_parse_python_version_flag() -> None:
    settings = parse_args(["--python-version", "3.9"])

    assert settings.python_version == (3, 9)


def test_parse_invalid_python_version_flag_will_fail() -> None:
    versions = ["3.10.8", "x.y", "-3.-8"]

    for version in versions:
        with pytest.raises(ValueError, match="version must be in form `x.y`"):
            parse_args(["--python-version", version])


def test_parse_python_version_flag_in_config_file() -> None:
    contents = """\
[tool.refurb]
python_version = "3.5"
"""

    config_file = parse_config_file(contents)

    assert config_file.python_version == (3, 5)


def test_enable_all_flag() -> None:
    assert parse_args(["--enable-all"]) == Settings(enable_all=True)


def test_enable_all_will_clear_any_previously_disabled_checks() -> None:
    settings = parse_args(["--disable", "FURB100", "--enable-all"])

    assert settings == Settings(enable_all=True)


def test_enable_all_in_config_file() -> None:
    config = """\
[tool.refurb]
enable_all = true
"""

    assert parse_config_file(config).enable_all


def test_enable_all_and_disable_all_are_mutually_exclusive() -> None:
    with pytest.raises(ValueError, match="can't be used at the same time"):
        Settings(enable_all=True, disable_all=True)


def test_merging_enable_all_field() -> None:
    config = """\
[tool.refurb]
enable = ["FURB100", "FURB101", "FURB102"]
disable = ["FURB100", "FURB103"]
"""

    config_file = parse_config_file(config)

    command_line_args = parse_args(["--enable-all", "--disable", "FURB105"])

    merged_settings = Settings.merge(config_file, command_line_args)

    assert merged_settings == Settings(enable_all=True, disable={ErrorCode(105)})


def test_parse_config_file_categories() -> None:
    config = """\
[tool.refurb]
enable = ["#category-a"]
disable = ["#category-b"]
ignore = ["#category-c"]
"""

    config_file = parse_config_file(config)

    assert config_file == Settings(
        enable={ErrorCategory("category-a")},
        disable={ErrorCategory("category-b")},
        ignore={ErrorCategory("category-c")},
    )


def test_parse_mypy_extra_args() -> None:
    settings = parse_args(["--", "mypy", "args", "here"])

    assert settings == Settings(mypy_args=["mypy", "args", "here"])


def test_parse_mypy_extra_args_in_config() -> None:
    config = """\
[tool.refurb]
mypy_args = ["some", "args"]
"""

    config_file = parse_config_file(config)

    assert config_file == Settings(mypy_args=["some", "args"])


def test_cli_args_override_mypy_args_in_config_file() -> None:
    config = """\
[tool.refurb]
mypy_args = ["some", "args"]
"""

    config_file = parse_config_file(config)

    cli_args = parse_args(["--", "new", "args"])
    merged = Settings.merge(config_file, cli_args)

    assert merged == Settings(mypy_args=["new", "args"])


def test_flags_which_support_comma_separated_cli_args() -> None:
    settings = parse_args(
        [
            "--enable",
            "100,101",
            "--disable",
            "102,103",
            "--ignore",
            "104,105",
        ]
    )

    assert settings == Settings(
        enable={ErrorCode(100), ErrorCode(101)},
        disable={ErrorCode(102), ErrorCode(103)},
        ignore={ErrorCode(104), ErrorCode(105)},
    )


def test_parse_amend_file_paths() -> None:
    config = """\
[tool.refurb]
ignore = ["FURB100"]

[[tool.refurb.amend]]
path = "some/file/path"
ignore = ["FURB101", "FURB102"]

[[tool.refurb.amend]]
path = "some/other/path"
ignore = [102, 103]
"""

    config_file = parse_config_file(config)

    assert config_file == Settings(
        ignore={
            ErrorCode(100),
            ErrorCode(101, path=Path("some/file/path")),
            ErrorCode(102, path=Path("some/file/path")),
            ErrorCode(102, path=Path("some/other/path")),
            ErrorCode(103, path=Path("some/other/path")),
        }
    )


def test_invalid_amend_field_fails() -> None:
    config = """\
[tool.refurb]
amend = "oops"
"""

    msg = r'"amend" field\(s\) must be a TOML table'

    with pytest.raises(ValueError, match=msg):
        parse_config_file(config)


def test_extra_fields_in_amend_table_fails() -> None:
    config = """\
[[tool.refurb.amend]]
path = "some/folder"
ignore = ["FURB123"]
extra = "data"
"""

    msg = 'only "path" and "ignore" fields are supported'

    with pytest.raises(ValueError, match=msg):
        parse_config_file(config)


def test_missing_or_malformed_fields_in_amend_table_fails() -> None:
    msg = '"path" or "ignore" fields are missing or malformed'

    config = """\
[[tool.refurb.amend]]
ignore = ["FURB123"]
"""

    with pytest.raises(ValueError, match=msg):
        parse_config_file(config)

    config = """\
[[tool.refurb.amend]]
path = "some/folder"
"""

    with pytest.raises(ValueError, match=msg):
        parse_config_file(config)

    config = """\
[[tool.refurb.amend]]
path = true
ignore = false
"""

    with pytest.raises(ValueError, match=msg):
        parse_config_file(config)


def test_extra_fields_config_file_fails() -> None:
    config = """\
[tool.refurb]
unknown = ""
fields = ""
"""

    msg = r"refurb: unknown field\(s\): unknown, fields"

    with pytest.raises(ValueError, match=msg):
        parse_config_file(config)


def test_incorrectly_typed_args_raises_error() -> None:
    tests = {
        "ignore = false": "must be a list",
        "enable = false": "must be a list",
        "disable = false": "must be a list",
        "load = false": "must be a list",
        "mypy_args = false": "must be a list",
        "quiet = []": "must be a bool",
        "disable_all = []": "must be a bool",
        "enable_all = []": "must be a bool",
        "python_version = false": "must be a string",
    }

    for test, expected in tests.items():
        config = f"[tool.refurb]\n{test}"

        with pytest.raises(ValueError, match=expected):
            parse_config_file(config)


def test_parse_empty_config_file() -> None:
    assert parse_config_file("") == Settings()


def test_parse_format_flag() -> None:
    assert parse_args(["--format", "github"]) == Settings(format="github")


def test_check_format_must_be_valid() -> None:
    msg = 'refurb: "oops" is not a valid format'

    with pytest.raises(ValueError, match=msg):
        parse_args(["--format", "oops"])


def test_parse_sort_by_flag() -> None:
    assert parse_args(["--sort", "error"]) == Settings(sort_by="error")


def test_check_sort_by_field_must_be_valid() -> None:
    msg = 'refurb: cannot sort by "oops"'

    with pytest.raises(ValueError, match=msg):
        parse_args(["--sort", "oops"])


def test_disallow_empty_string_in_cli() -> None:
    tests = [
        [""],
        ["file.py", ""],
    ]

    for test in tests:
        msg = "refurb: argument cannot be empty"

        with pytest.raises(ValueError, match=msg):
            parse_args(test)


def test_ignored_flags_cause_error() -> None:
    tests = [
        ["--help", "file.py"],
        ["--version", "file.py"],
        ["-h", "file.py"],
        ["file.py", "--help"],
        ["--version", "file.py"],
        ["file.py", "-h"],
    ]

    for test in tests:
        msg = f"refurb: unexpected value before/after `{test[0]}`"

        with pytest.raises(ValueError, match=msg):
            parse_args(test)


def test_generate_subcommand_is_ignored_if_other_files_are_passed() -> None:
    assert parse_args(["gen", "something"]) == Settings(files=["gen", "something"])


def test_parse_verbose_flag() -> None:
    assert parse_args(["--verbose"]) == Settings(verbose=True)
    assert parse_args(["-v"]) == Settings(verbose=True)


def test_parse_timing_stats_flag() -> None:
    assert parse_args(["--timing-stats", "file"]) == Settings(timing_stats=Path("file"))


def test_parse_timing_stats_flag_without_arg_is_an_error() -> None:
    with pytest.raises(ValueError, match='refurb: missing argument after "--timing-stats"'):
        parse_args(["--timing-stats"])


def test_parse_no_color_flag() -> None:
    assert parse_args(["--no-color"]) == Settings(color=False)


def test_no_color_env_var_disables_color() -> None:
    with patch.dict(os.environ, {"NO_COLOR": "1"}):
        settings = Settings()

        assert not settings.color
