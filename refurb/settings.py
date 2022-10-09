import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

if sys.version_info >= (3, 11):
    import tomllib  # pragma: no cover
else:
    import tomli as tomllib

from .error import ErrorCode


@dataclass
class Settings:
    files: list[str] | None = None
    explain: ErrorCode | None = None
    ignore: set[ErrorCode] | None = None
    load: list[str] | None = None
    enable: set[ErrorCode] | None = None
    debug: bool = False
    generate: bool = False
    help: bool = False
    version: bool = False
    quiet: bool = False
    config_file: str | None = None


ERROR_ID_REGEX = re.compile("^([A-Z]{3,4})?(\\d{3})$")


def parse_error_id(err: str) -> ErrorCode:
    if match := ERROR_ID_REGEX.match(err):
        groups = match.groups()

        return ErrorCode(prefix=groups[0] or "FURB", id=int(groups[1]))

    raise ValueError(f'refurb: "{err}" must be in form FURB123 or 123')


def parse_config_file(contents: str) -> Settings:
    config = tomllib.loads(contents)

    if tool := config.get("tool"):
        if settings := tool.get("refurb"):
            ignore = set(
                parse_error_id(str(x)) for x in settings.get("ignore", [])
            )

            enable = set(
                parse_error_id(str(x)) for x in settings.get("enable", [])
            )

            return Settings(
                ignore=ignore or None,
                enable=enable or None,
                load=settings.get("load"),
                quiet=settings.get("quiet", False),
            )

    return Settings()


def parse_command_line_args(args: list[str]) -> Settings:
    if not args or args[0] in ("--help", "-h"):
        return Settings(help=True)

    if args[0] in ("--version", "-v"):
        return Settings(version=True)

    if args[0] == "gen":
        return Settings(generate=True)

    iargs = iter(args)

    settings = Settings()
    files: list[str] = []
    ignore: set[ErrorCode] = set()
    load: list[str] = []
    enable: set[ErrorCode] = set()

    def get_next_arg(arg: str, args: Iterator[str]) -> str:
        if (value := next(args, None)) is not None:
            return value

        raise ValueError(f'refurb: missing argument after "{arg}"')

    for arg in iargs:
        if arg == "--debug":
            settings.debug = True

        elif arg == "--quiet":
            settings.quiet = True

        elif arg == "--explain":
            settings.explain = parse_error_id(get_next_arg(arg, iargs))

        elif arg == "--ignore":
            ignore.add(parse_error_id(get_next_arg(arg, iargs)))

        elif arg == "--enable":
            enable.add(parse_error_id(get_next_arg(arg, iargs)))

        elif arg == "--load":
            load.append(get_next_arg(arg, iargs))

        elif arg == "--config-file":
            settings.config_file = get_next_arg(arg, iargs)

        elif arg.startswith("-"):
            raise ValueError(f'refurb: unsupported option "{arg}"')

        else:
            files.append(arg)

    settings.files = files or None
    settings.ignore = ignore or None
    settings.enable = enable or None
    settings.load = load or None

    return settings


def merge_settings(command_line: Settings, config_file: Settings) -> Settings:
    if not command_line.ignore:
        command_line.ignore = config_file.ignore

    if not command_line.enable:
        command_line.enable = config_file.enable

    if not command_line.load:
        command_line.load = config_file.load

    return command_line


def load_settings(args: list[str]) -> Settings:
    cli_args = parse_command_line_args(args)

    file = Path(cli_args.config_file or "pyproject.toml")

    config_file = (
        parse_config_file(file.read_text()) if file.exists() else Settings()
    )

    return merge_settings(cli_args, config_file)
