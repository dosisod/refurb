from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

if sys.version_info >= (3, 11):
    import tomllib  # pragma: no cover
else:
    import tomli as tomllib  # pragma: no cover

from .error import ErrorCategory, ErrorClassifier, ErrorCode


def get_python_version() -> tuple[int, int]:
    return sys.version_info[:2]


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
    format: Literal["text", "github", None] | None = None
    sort_by: Literal["filename", "error"] | None = None

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
            python_version=new.python_version or old.python_version,
            mypy_args=new.mypy_args or old.mypy_args,
            format=new.format or old.format,
            sort_by=new.sort_by or old.sort_by,
        )

    def get_python_version(self) -> tuple[int, int]:
        return self.python_version or get_python_version()


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


def validate_format(format: str) -> Literal["github", "text"]:
    if format in ("github", "text"):
        return format  # type: ignore

    raise ValueError(f'refurb: "{format}" is not a valid format')


def validate_sort_by(sort_by: str) -> Literal["filename", "error"]:
    if sort_by in ("filename", "error"):
        return sort_by  # type: ignore

    raise ValueError(f'refurb: cannot sort by "{sort_by}"')


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


T = TypeVar("T")


def pop_type(  # type: ignore[misc]
    ty: type[T], type_name: str = ""
) -> Callable[..., T]:
    def inner(config: dict[str, Any], name: str) -> T:  # type: ignore[misc]
        x = config.pop(name, ty())

        if isinstance(x, ty):
            return x

        raise ValueError(
            f'refurb: "{name}" must be a {type_name or ty.__name__}'
        )

    return inner


pop_list = pop_type(list)
pop_bool = pop_type(bool)
pop_str = pop_type(str, "string")


def parse_config_file(contents: str) -> Settings:
    tool = tomllib.loads(contents).get("tool")

    if not tool:
        return Settings()

    config = tool.get("refurb")

    if not config:
        return Settings()

    settings = Settings()

    settings.load = pop_list(config, "load")
    settings.quiet = pop_bool(config, "quiet")
    settings.disable_all = pop_bool(config, "disable_all")
    settings.enable_all = pop_bool(config, "enable_all")

    enable = pop_list(config, "enable")
    disable = pop_list(config, "disable")
    settings.enable = {parse_error_classifier(str(x)) for x in enable}
    settings.disable = {parse_error_classifier(str(x)) for x in disable}
    settings.enable -= settings.disable

    ignore = pop_list(config, "ignore")
    settings.ignore = {parse_error_classifier(str(x)) for x in ignore}

    mypy_args = pop_list(config, "mypy_args")
    settings.mypy_args = [str(x) for x in mypy_args]

    if "python_version" in config:
        version = pop_str(config, "python_version")

        settings.python_version = parse_python_version(version)

    if "format" in config:
        settings.format = validate_format(pop_str(config, "format"))

    if "sort_by" in config:
        settings.sort_by = validate_sort_by(pop_str(config, "sort_by"))

    amendments: list[dict[str, Any]] = config.pop("amend", [])  # type: ignore

    if not isinstance(amendments, list):
        raise ValueError('refurb: "amend" field(s) must be a TOML table')

    for amendment in amendments:
        settings.ignore.update(parse_amendment(amendment))

    if config:
        raise ValueError(
            f"refurb: unknown field(s): {', '.join(config.keys())}"
        )

    return settings


def parse_command_line_args(args: list[str]) -> Settings:
    if not args:
        return Settings(help=True)

    if len(args) == 1 and args[0] == "gen":
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

        elif arg in ("--help", "-h"):
            settings.help = True

        elif arg in ("--version", "-v"):
            settings.version = True

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

        elif arg == "--format":
            settings.format = validate_format(get_next_arg(arg, iargs))

        elif arg == "--sort":
            settings.sort_by = validate_sort_by(get_next_arg(arg, iargs))

        elif arg == "--":
            settings.mypy_args = list(iargs)

        elif arg.startswith("-"):
            raise ValueError(f'refurb: unsupported option "{arg}"')

        elif arg:
            settings.files.append(arg)

        else:
            raise ValueError("refurb: argument cannot be empty")

    if len(args) > 1 and (settings.help or settings.version):
        msg = f"refurb: unexpected value before/after `{args[0]}`"

        raise ValueError(msg)

    return settings


def load_settings(args: list[str]) -> Settings:
    cli_args = parse_command_line_args(args)

    file = Path(cli_args.config_file or "pyproject.toml")

    try:
        config_file = parse_config_file(file.read_text())

    except IsADirectoryError as ex:
        raise ValueError(f'refurb: "{file}" is a directory') from ex

    except FileNotFoundError as ex:
        if cli_args.config_file:
            raise ValueError(f'refurb: "{file}" was not found') from ex

        config_file = Settings()  # pragma: no cover

    return Settings.merge(config_file, cli_args)
