import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

if sys.version_info >= (3, 11):
    import tomllib  # pragma: no cover
else:
    import tomli as tomllib

from .error import ErrorCode


@dataclass
class Settings:
    files: list[str] = field(default_factory=list)
    explain: ErrorCode | None = None
    ignore: set[ErrorCode] = field(default_factory=set)
    load: list[str] = field(default_factory=list)
    enable: set[ErrorCode] = field(default_factory=set)
    disable: set[ErrorCode] = field(default_factory=set)
    debug: bool = False
    generate: bool = False
    help: bool = False
    version: bool = False
    quiet: bool = False
    config_file: str | None = None

    @staticmethod
    def merge(old: "Settings", new: "Settings") -> "Settings":
        enable = old.enable | new.enable
        disable = old.disable | new.disable

        enable -= disable

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
            quiet=old.quiet or new.quiet,
            config_file=old.config_file or new.config_file,
        )


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

            disable = set(
                parse_error_id(str(x)) for x in settings.get("disable", [])
            )

            return Settings(
                ignore=ignore,
                enable=enable - disable,
                disable=disable,
                load=settings.get("load", []),
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
            settings.ignore.add(parse_error_id(get_next_arg(arg, iargs)))

        elif arg == "--enable":
            error_code = parse_error_id(get_next_arg(arg, iargs))

            settings.enable.add(error_code)
            settings.disable.discard(error_code)

        elif arg == "--disable":
            error_code = parse_error_id(get_next_arg(arg, iargs))

            settings.disable.add(error_code)
            settings.enable.discard(error_code)

        elif arg == "--load":
            settings.load.append(get_next_arg(arg, iargs))

        elif arg == "--config-file":
            settings.config_file = get_next_arg(arg, iargs)

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
