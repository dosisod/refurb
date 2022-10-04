import re
from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib  # type: ignore
except ImportError:
    import tomli as tomllib  # type: ignore


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
    files: list[str] = []
    ignore: set[ErrorCode] = set()
    enable: set[ErrorCode] = set()
    load: list[str] = []
    explain: ErrorCode | None = None
    debug = False
    quiet = False

    for arg in iargs:
        if arg == "--debug":
            debug = True

        elif arg == "--quiet":
            quiet = True

        elif arg == "--explain":
            value = next(iargs, None)

            if value is None:
                raise ValueError(f'refurb: missing argument after "{arg}"')

            explain = parse_error_id(value)

        elif arg == "--ignore":
            value = next(iargs, None)

            if value is None:
                raise ValueError(f'refurb: missing argument after "{arg}"')

            ignore.add(parse_error_id(value))

        elif arg == "--enable":
            value = next(iargs, None)

            if value is None:
                raise ValueError(f'refurb: missing argument after "{arg}"')

            enable.add(parse_error_id(value))

        elif arg == "--load":
            value = next(iargs, None)

            if value is None:
                raise ValueError(f'refurb: missing argument after "{arg}"')

            load.append(value)

        elif arg.startswith("-"):
            raise ValueError(f'refurb: unsupported option "{arg}"')

        else:
            files.append(arg)

    return Settings(
        files=files or None,
        ignore=ignore or None,
        enable=enable or None,
        load=load or None,
        debug=debug,
        explain=explain,
        quiet=quiet,
    )


def merge_settings(command_line: Settings, config_file: Settings) -> Settings:
    if not command_line.ignore:
        command_line.ignore = config_file.ignore

    if not command_line.enable:
        command_line.enable = config_file.enable

    if not command_line.load:
        command_line.load = config_file.load

    return command_line


def load_settings(args: list[str]) -> Settings:
    file = Path("pyproject.toml")

    config_file = (
        parse_config_file(file.read_text()) if file.exists() else Settings()
    )

    return merge_settings(parse_command_line_args(args), config_file)
