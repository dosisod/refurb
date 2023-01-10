import re
from functools import cache
from importlib import metadata
from io import StringIO
from pathlib import Path
from typing import Sequence

from mypy.build import build
from mypy.errors import CompileError
from mypy.main import process_options

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
              [--disable err] [--disable-all] [--enable-all]
              [--config-file path] [--python-version version] src [srcs...]
       refurb [--help | -h]
       refurb [--version | -v]
       refurb --explain err
       refurb gen

Command Line Options:

--help, -h            This help menu.
--version, -v         Print version information.
--ignore err          Ignore an error. Can be repeated.
--load module         Add a module to the list of paths to be searched when looking for checks. Can be repeated.
--debug               Print the AST representation of all files that where checked.
--quiet               Suppress default "--explain" suggestion when an error occurs.
--enable err          Load a check which is disabled by default.
--disable err         Disable loading a check which is enabled by default.
--config-file file    Load "file" instead of the default config file.
--explain err         Print the explaination/documentation from a given error code.
--disable-all         Disable all checks by default.
--enable-all          Enable all checks by default.
--python-version x.y  Version of the Python code being checked.
src                   A file or folder.


Subcommands:

gen              Generate boilerplate code for a new check, meant for
                 developers.
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

    line = get_source_lines(error.filename)[error.line - 1]

    if comment := re.search("# noqa(: [A-Z]{3,4}\\d{3})?$", line):
        ignore = comment.group(1)
        error_code = str(ErrorCode.from_error(type(error)))

        if not ignore or ignore[2:] == error_code:
            return True

    return False


def is_ignored_via_amend(error: Error, settings: Settings) -> bool:
    assert error.filename

    path = Path(error.filename).resolve()
    error_code = ErrorCode.from_error(type(error))
    config_root = (
        Path(settings.config_file).parent if settings.config_file else Path()
    )

    for ignore in settings.ignore:
        if ignore.path:
            ignore_path = (config_root / ignore.path).resolve()

            if path.is_relative_to(ignore_path):
                if isinstance(ignore, ErrorCode):
                    return str(ignore) == str(error_code)

                return ignore.value in error.categories

    return False


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

    if settings.python_version:
        opt.python_version = settings.python_version  # pragma: no cover

    try:
        result = build(files, options=opt)

    except CompileError as e:
        return [re.sub("^mypy: ", "refurb: ", msg) for msg in e.messages]

    errors: list[Error | str] = []

    for file in files:
        if tree := result.graph[file.module].tree:
            if settings.debug:
                errors.append(str(tree))

            checks = load_checks(settings)
            visitor = RefurbVisitor(checks, settings)

            tree.accept(visitor)

            for error in visitor.errors:
                error.filename = file.path

            errors += visitor.errors

    return sorted(
        [
            error
            for error in errors
            if not should_ignore_error(error, settings)
        ],
        key=sort_errors,
    )


def sort_errors(
    error: Error | str,
) -> tuple[str, int, int, str, int] | tuple[str, str]:
    if isinstance(error, str):
        return ("", error)

    return (
        error.filename or "",
        error.line,
        error.column,
        error.prefix,
        error.code,
    )


def format_errors(errors: Sequence[Error | str], quiet: bool) -> str:
    done = "\n".join((str(error) for error in errors))

    if not quiet and any(isinstance(error, Error) for error in errors):
        done += "\n\nRun `refurb --explain ERR` to further explain an error. Use `--quiet` to silence this message"

    return done


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
        print(explain(settings.explain, settings.load or []))

        return 0

    try:
        errors = run_refurb(settings)

    except TypeError as e:
        print(e)
        return 1

    if formatted_errors := format_errors(errors, settings.quiet):
        print(formatted_errors)

    return 1 if errors else 0
