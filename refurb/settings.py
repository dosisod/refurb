from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib  # type: ignore
except ImportError:
    import tomli as tomllib  # type: ignore


@dataclass
class Settings:
    files: list[str] | None = None
    explain: int | None = None
    ignore: set[int] | None = None
    load: list[str] | None = None
    debug: bool = False
    generate: bool = False


def parse_error_id(err: str) -> int:
    id = err.replace("FURB", "")

    if id.isdigit():
        return int(id)

    raise ValueError(f'refurb: "{id}" must be in form FURB123 or 123')


def parse_config_file(contents: str) -> Settings:
    config = tomllib.loads(contents)

    if tool := config.get("tool"):
        if settings := tool.get("refurb"):
            ignore = set(
                parse_error_id(str(x)) for x in settings.get("ignore")
            )

            return Settings(ignore=ignore, load=settings.get("load"))

    return Settings()


def parse_command_line_args(args: list[str]) -> Settings:
    if not args:
        raise ValueError("refurb: no arguments passed")

    if args[0] == "gen":
        return Settings(generate=True)

    if args[0] == "--explain":
        if len(args) != 2:
            raise ValueError("usage: refurb --explain ID")

        return Settings(explain=parse_error_id(args[1]))

    iargs = iter(args)
    files: list[str] = []
    ignore: set[int] = set()
    load: list[str] = []
    debug = False

    for arg in iargs:
        if arg == "--debug":
            debug = True

        elif arg == "--ignore":
            value = next(iargs, None)

            if value is None:
                raise ValueError(f'refurb: missing argument after "{arg}"')

            ignore.add(parse_error_id(value))

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
        files=files, ignore=ignore or None, load=load or None, debug=debug
    )


def merge_settings(command_line: Settings, config_file: Settings) -> Settings:
    if not command_line.ignore:
        command_line.ignore = config_file.ignore

    if not command_line.load:
        command_line.load = config_file.load

    return command_line


def load_settings(args: list[str]) -> Settings:
    file = Path("pyproject.toml")

    config_file = (
        parse_config_file(file.read_text()) if file.exists() else Settings()
    )

    return merge_settings(parse_command_line_args(args), config_file)
