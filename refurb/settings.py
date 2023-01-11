from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Iterator

if sys.version_info >= (3, 11):
    import tomllib  # pragma: no cover
else:
    import tomli as tomllib  # pragma: no cover

from .error import ErrorCategory, ErrorClassifier, ErrorCode


@dataclass
class Settings:
    files: list[str] = field(default_factory=list)
    explain: ErrorCode | None = None
    ignore: set[ErrorClassifier] = field(default_factory=set)
    load: list[str] = field(default_factory=list)
    enable: set[ErrorClassifier] = field(default_factory=set)
    disable: set[ErrorClassifier] = field(default_factory=set)
    debug: bool = False
    generate: bool = False
    help: bool = False
    version: bool = False
    quiet: bool = False
    enable_all: bool = False
    disable_all: bool = False
    config_file: str | None = None
    python_version: tuple[int, int] | None = None
    mypy_args: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.enable_all and self.disable_all:
            raise ValueError(
                'refurb: "enable all" and "disable all" can\'t be used at the same time'  # noqa: E501
            )

    @staticmethod
    def merge(old: Settings, new: Settings) -> Settings:
        if not old.disable_all and new.disable_all:
            enable = new.enable
            disable = set()

        elif not old.enable_all and new.enable_all:
            disable = new.disable
            enable = set()

        else:
            disable = old.disable | new.disable
            enable = (old.enable | new.enable) - disable

        return Settings(
            files=old.files + new.files,
            explain=old.explain or new.explain,
            ignore=old.ignore | new.ignore,
            enable=enable,
            disable=disable,
            load=old.load + new.load,
            debug=old.debug or new.debug,
            generate=old.generate or new.generate,
            help=old.help or new.help,
            version=old.version or new.version,
            disable_all=old.disable_all or new.disable_all,
            enable_all=old.enable_all or new.enable_all,
            quiet=old.quiet or new.quiet,
            config_file=old.config_file or new.config_file,
            python_version=old.python_version or new.python_version,
            mypy_args=new.mypy_args or old.mypy_args,
        )


ERROR_ID_REGEX = re.compile("^([A-Z]{3,4})?(\\d{3})$")


def parse_error_classifier(err: str) -> ErrorCategory | ErrorCode:
    return parse_error_category(err) or parse_error_id(err)


def parse_error_category(err: str) -> ErrorCategory | None:
    return ErrorCategory(err[1:]) if err.startswith("#") else None


def parse_error_id(err: str) -> ErrorCode:
    if match := ERROR_ID_REGEX.match(err):
        groups = match.groups()

        return ErrorCode(prefix=groups[0] or "FURB", id=int(groups[1]))

    raise ValueError(f'refurb: "{err}" must be in form FURB123 or 123')


def parse_python_version(version: str) -> tuple[int, int]:
    nums = version.split(".")

    if len(nums) == 2 and all(num.isnumeric() for num in nums):
        return tuple(int(num) for num in nums)[:2]  # type: ignore

    raise ValueError("refurb: version must be in form `x.y`")


def parse_amend_error(err: str, path: Path) -> ErrorClassifier:
    classifier = parse_error_classifier(err)

    return replace(classifier, path=path)


def parse_amendment(  # type: ignore
    amendment: dict[str, Any]
) -> set[ErrorClassifier]:
    match amendment:
        case {"path": str(path), "ignore": list(ignored), **extra}:
            if extra:
                raise ValueError(
                    'refurb: only "path" and "ignore" fields are supported'
                )

            return {
                parse_amend_error(str(error), Path(path)) for error in ignored
            }

    raise ValueError(
        'refurb: "path" or "ignore" fields are missing or malformed'
    )


def parse_config_file(contents: str) -> Settings:
    tool = tomllib.loads(contents).get("tool")

    if not tool:
        return Settings()

    config = tool.get("refurb")

    if not config:
        return Settings()

    ignore = {parse_error_classifier(str(x)) for x in config.get("ignore", [])}
    enable = {parse_error_classifier(str(x)) for x in config.get("enable", [])}

    disable = {
        parse_error_classifier(str(x)) for x in config.get("disable", [])
    }

    version = config.get("python_version")
    python_version = parse_python_version(version) if version else None
    mypy_args = [str(arg) for arg in config.get("mypy_args", [])]

    amendments: list[dict[str, Any]] = config.get("amend", [])  # type: ignore

    if not isinstance(amendments, list):
        raise ValueError('refurb: "amend" field(s) must be a TOML table')

    for amendment in amendments:
        ignore.update(parse_amendment(amendment))

    return Settings(
        ignore=ignore,
        enable=enable - disable,
        disable=disable,
        load=config.get("load", []),
        quiet=config.get("quiet", False),
        disable_all=config.get("disable_all", False),
        enable_all=config.get("enable_all", False),
        python_version=python_version,
        mypy_args=mypy_args,
    )


def parse_command_line_args(args: list[str]) -> Settings:
    if not args or args[0] in ("--help", "-h"):
        return Settings(help=True)

    if args[0] in ("--version", "-v"):
        return Settings(version=True)

    if args[0] == "gen":
        return Settings(generate=True)

    iargs = iter(args)

    settings = Settings()

    def get_next_arg(arg: str, args: Iterator[str]) -> str:
        if (value := next(args, None)) is not None:
            return value

        raise ValueError(f'refurb: missing argument after "{arg}"')

    for arg in iargs:
        if arg == "--debug":
            settings.debug = True

        elif arg == "--quiet":
            settings.quiet = True

        elif arg == "--disable-all":
            settings.enable.clear()
            settings.disable_all = True

        elif arg == "--enable-all":
            settings.disable.clear()
            settings.enable_all = True

        elif arg == "--explain":
            settings.explain = parse_error_id(get_next_arg(arg, iargs))

        elif arg == "--ignore":
            classifiers = get_next_arg(arg, iargs).split(",")

            settings.ignore.update(map(parse_error_classifier, classifiers))

        elif arg == "--enable":
            error_codes = {
                parse_error_classifier(classifier)
                for classifier in get_next_arg(arg, iargs).split(",")
            }

            settings.enable |= error_codes
            settings.disable -= error_codes

        elif arg == "--disable":
            error_codes = {
                parse_error_classifier(classifier)
                for classifier in get_next_arg(arg, iargs).split(",")
            }

            settings.disable |= error_codes
            settings.enable -= error_codes

        elif arg == "--load":
            settings.load.append(get_next_arg(arg, iargs))

        elif arg == "--config-file":
            settings.config_file = get_next_arg(arg, iargs)

        elif arg == "--python-version":
            version = get_next_arg(arg, iargs)

            settings.python_version = parse_python_version(version)

        elif arg == "--":
            settings.mypy_args = list(iargs)

        elif arg.startswith("-"):
            raise ValueError(f'refurb: unsupported option "{arg}"')

        else:
            settings.files.append(arg)

    return settings


def load_settings(args: list[str]) -> Settings:
    cli_args = parse_command_line_args(args)

    file = Path(cli_args.config_file or "pyproject.toml")

    config_file = (
        parse_config_file(file.read_text()) if file.exists() else Settings()
    )

    return Settings.merge(config_file, cli_args)
