import json
import re
import time
from collections.abc import Callable, Sequence
from contextlib import suppress
from functools import cache, partial
from importlib import metadata
from io import StringIO
from operator import itemgetter
from pathlib import Path
from tempfile import mkstemp

from mypy.build import build
from mypy.errors import CompileError
from mypy.main import process_options

from . import types
from .error import Error, ErrorCode
from .explain import explain
from .gen import main as generate
from .loader import load_checks
from .settings import Settings, load_settings
from .visitor import RefurbVisitor


def usage() -> None:
    print(
        """\
usage: refurb [--ignore err] [--load path] [--debug] [--quiet] [--enable err]
              [--disable err] [--enable-all] [--disable-all]
              [--config-file path] [--python-version version] [--verbose | -v]
              [--format format] [--sort sort] [--timing-stats file]
              SRC [SRCS...] [-- MYPY_ARGS]
       refurb [--help | -h]
       refurb [--version]
       refurb --explain err
       refurb gen

Command Line Options:

--help, -h            This help menu.
--version             Print version information.
--ignore err          Ignore an error. Can be repeated.
--load module         Add a module to the list of paths to be searched when looking for checks. Can be repeated.
--debug               Print the AST representation of all files that where checked.
--quiet               Suppress default "--explain" suggestion when an error occurs.
--enable err          Load a check which is disabled by default.
--disable err         Disable loading a check which is enabled by default.
--config-file file    Load "file" instead of the default config file.
--explain err         Print the explanation/documentation from a given error code.
--disable-all         Disable all checks by default.
--enable-all          Enable all checks by default.
--python-version x.y  Version of the Python code being checked.
--verbose             Increase verbosity.
--format format       Output errors in specified format. Can be "text" or "github".
--sort sort           Sort errors by sort. Can be "filename" or "error".
--timing-stats file   Export timing information (as JSON) to file.

Positional Args:

SRC                   A list of files or folders to check.
MYPY_ARGS             Extra args to be passed directly to Mypy.


Subcommands:

gen              Generate boilerplate code for a new check. Useful for developers.
"""
    )


def version() -> str:  # pragma: no cover
    refurb_version = metadata.version("refurb")
    mypy_version = metadata.version("mypy")

    return f"Refurb: v{refurb_version}\nMypy: v{mypy_version}"


@cache
def get_source_lines(filepath: str) -> list[str]:
    return Path(filepath).read_text("utf8").splitlines()


def is_ignored_via_comment(error: Error) -> bool:
    assert error.filename

    line = get_source_lines(error.filename)[error.line - 1].rstrip()

    if comment := re.search(r"""# noqa(: [^'"]*)?$""", line):
        ignore = str(ErrorCode.from_error(type(error)))
        error_codes = comment.group(1)

        return not error_codes or any(
            error_code == ignore for error_code in error_codes[2:].replace(",", " ").split(" ")
        )

    return False


def is_ignored_via_amend(error: Error, settings: Settings) -> bool:
    assert error.filename

    path = Path(error.filename).resolve()
    error_code = str(ErrorCode.from_error(type(error)))
    config_root = Path(settings.config_file).parent if settings.config_file else Path()

    errors_to_ignore = set[str]()
    categories_to_ignore = set[str]()

    for ignore in settings.ignore:
        if ignore.path:
            ignore_path = (config_root / ignore.path).resolve()

            if path.is_relative_to(ignore_path):
                if isinstance(ignore, ErrorCode):
                    errors_to_ignore.add(str(ignore))
                else:
                    categories_to_ignore.add(ignore.value)

    return error_code in errors_to_ignore or bool(
        categories_to_ignore.intersection(error.categories)
    )


def should_ignore_error(error: Error | str, settings: Settings) -> bool:
    if isinstance(error, str):
        return False

    return (
        not error.filename
        or is_ignored_via_comment(error)
        or is_ignored_via_amend(error, settings)
    )


def run_refurb(settings: Settings) -> Sequence[Error | str]:
    stdout = StringIO()
    stderr = StringIO()

    try:
        args = [
            *settings.files,
            *settings.mypy_args,
            "--exclude",
            ".*\\.pyi",
            "--explicit-package-bases",
            "--namespace-packages",
        ]

        files, opt = process_options(args, stdout=stdout, stderr=stderr)

    except SystemExit:
        lines = ["refurb: " + err for err in stderr.getvalue().splitlines()]

        return lines + stdout.getvalue().splitlines()

    finally:
        stdout.close()
        stderr.close()

    opt.incremental = True
    opt.fine_grained_incremental = True
    opt.cache_fine_grained = True
    opt.allow_redefinition = True
    opt.local_partial_types = True
    opt.python_version = settings.get_python_version()

    mypy_timing_stats = Path(mkstemp()[1]) if settings.timing_stats else None
    opt.timing_stats = str(mypy_timing_stats) if mypy_timing_stats else None

    try:
        start = time.time()

        result = build(files, options=opt)

        mypy_build_time = time.time() - start

    except CompileError as e:
        return [re.sub(r"^mypy: ", "refurb: ", msg) for msg in e.messages]

    errors: list[Error | str] = []
    checks = load_checks(settings)

    refurb_timing_stats_in_ms: dict[str, int] = {}

    builtins_file = result.graph["builtins"].tree
    assert builtins_file

    # Store the builtins module AST node as a global variable so we can access it later to create
    # certain type nodes. This isn't the most elegant solution, but is more lightweight compared to
    # creating a new type checker instance.
    types.BUILTINS_MYPY_FILE = builtins_file

    for file in files:
        tree = result.graph[file.module].tree

        assert tree

        if settings.debug:
            errors.append(str(tree))

        start = time.time()

        visitor = RefurbVisitor(checks, settings)

        # See: https://github.com/dosisod/refurb/issues/302
        with suppress(RecursionError):
            visitor.accept(tree)

        elapsed = time.time() - start

        refurb_timing_stats_in_ms[file.module] = int(elapsed * 1_000)

        for error in visitor.errors:
            error.filename = file.path

        errors += visitor.errors

    output_timing_stats(
        settings,
        mypy_build_time,
        mypy_timing_stats,
        refurb_timing_stats_in_ms,
    )

    if mypy_timing_stats:
        mypy_timing_stats.unlink()

    return sorted(
        [error for error in errors if not should_ignore_error(error, settings)],
        key=partial(sort_errors, settings=settings),
    )


def sort_errors(error: Error | str, settings: Settings) -> tuple[str | int, ...]:
    if isinstance(error, str):
        return ("", error)

    if settings.sort_by == "error":
        return (
            error.prefix,
            error.code,
            error.filename or "",
            error.line,
            error.column,
        )

    return (
        error.filename or "",
        error.line,
        error.column,
        error.prefix,
        error.code,
    )


def format_as_github_annotation(error: Error | str) -> str:
    if isinstance(error, str):
        return f"::error title=Refurb Error::{error}"

    assert error.filename

    file = Path(error.filename).resolve().relative_to(Path.cwd())

    return "::error " + ",".join(
        [
            f"line={error.line}",
            f"col={error.column + 1}",
            f"title=Refurb {error.prefix}{error.code}",
            f"file={file}::{error.msg}",
        ]
    )


ERROR_DIFF_PATTERN = re.compile(r"`([^`]*)`([^`]*)`([^`]*)`")


def format_with_color(error: Error | str) -> str:
    if isinstance(error, str):
        return error

    blue = "\x1b[94m"
    yellow = "\x1b[33m"
    gray = "\x1b[90m"
    green = "\x1b[92m"
    red = "\x1b[91m"
    reset = "\x1b[0m"

    # Add red/green color for diffs, assuming the 2 pairs of backticks are in the form:
    # Replace `old` with `new`
    if error.msg.count("`") == 4:
        parts = [
            f"{gray}`{red}\\1{gray}`{reset}",
            "\\2",
            f"{gray}`{green}\\3{gray}`{reset}",
        ]

        error.msg = ERROR_DIFF_PATTERN.sub("".join(parts), error.msg)

    parts = [
        f"{blue}{error.filename}{reset}",
        f"{gray}:{error.line}:{error.column + 1}{reset}",
        " ",
        f"{yellow}[{error.prefix}{error.code}]{reset}",
        f"{gray}:{reset}",
        " ",
        error.msg,
    ]

    return "".join(parts)


def format_errors(errors: Sequence[Error | str], settings: Settings) -> str:
    if settings.format == "github":
        formatter: Callable[[Error | str], str] = format_as_github_annotation
    elif settings.color:
        formatter = format_with_color
    else:
        formatter = str

    done = "\n".join(formatter(error) for error in errors)

    if not settings.quiet and any(isinstance(err, Error) for err in errors):
        done += "\n\nRun `refurb --explain ERR` to further explain an error. Use `--quiet` to silence this message"

    return done


def output_timing_stats(
    settings: Settings,
    mypy_total_time_spent: float,
    mypy_timing_stats: Path | None,
    refurb_timing_stats_in_ms: dict[str, int],
) -> None:
    if not settings.timing_stats:
        return

    assert mypy_timing_stats

    mypy_stats: dict[str, int] = {}
    lines = mypy_timing_stats.read_text().splitlines()

    for line in lines:
        module, micro_seconds = line.split()

        mypy_stats[module] = int(micro_seconds) // 1_000

    data = {
        "mypy_total_time_spent_in_ms": int(mypy_total_time_spent * 1_000),
        "mypy_time_spent_parsing_modules_in_ms": dict(
            sorted(mypy_stats.items(), key=itemgetter(1), reverse=True)
        ),
        "refurb_time_spent_checking_file_in_ms": dict(
            sorted(
                refurb_timing_stats_in_ms.items(),
                key=itemgetter(1),
                reverse=True,
            )
        ),
    }

    settings.timing_stats.write_text(json.dumps(data, separators=(",", ":")))


def main(args: list[str]) -> int:
    try:
        settings = load_settings(args)

    except ValueError as e:
        print(e)
        return 1

    if settings.help:
        usage()

        return 0

    if settings.version:
        print(version())

        return 0

    if settings.generate:
        generate()

        return 0

    if settings.explain:
        print(explain(settings))

        return 0

    try:
        errors = run_refurb(settings)

    except TypeError as e:
        print(e)
        return 1

    if formatted_errors := format_errors(errors, settings):
        print(formatted_errors)

    return 1 if errors else 0
