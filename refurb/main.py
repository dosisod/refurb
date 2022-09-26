import re
from functools import cache
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


@cache
def get_source_lines(filepath: str) -> list[str]:
    return Path(filepath).read_text().splitlines()


def ignored_via_comment(error: Error | str) -> bool:
    if isinstance(error, str) or not error.filename:
        return False

    line = get_source_lines(error.filename)[error.line - 1]

    if comment := re.search("# noqa(: [A-Z]{3,4}\\d{3})?$", line):
        ignore = comment.group(1)
        error_code = str(ErrorCode.from_error(type(error)))

        if not ignore or ignore[2:] == error_code:
            return True

    return False


def run_refurb(settings: Settings) -> Sequence[Error | str]:
    stderr = StringIO()

    try:
        files, opt = process_options(settings.files or [], stderr=stderr)

    except SystemExit:
        return ["refurb: " + err for err in stderr.getvalue().splitlines()]

    finally:
        stderr.close()

    opt.incremental = True
    opt.fine_grained_incremental = True
    opt.cache_fine_grained = True

    try:
        result = build(files, options=opt)

    except CompileError as e:
        return [msg.replace("mypy", "refurb") for msg in e.messages]

    errors: list[Error | str] = []

    for file in files:
        if tree := result.graph[file.module].tree:
            if settings.debug:
                errors.append(str(tree))

            checks = load_checks(settings.ignore or set(), settings.load or [])
            visitor = RefurbVisitor(checks)

            tree.accept(visitor)

            for error in visitor.errors:
                error.filename = file.path

            errors += visitor.errors

    return sorted(
        [error for error in errors if not ignored_via_comment(error)],
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


def main(args: list[str]) -> int:
    try:
        settings = load_settings(args)

    except ValueError as e:
        print(e)
        return 1

    if settings.generate:
        generate()

        return 0

    if settings.explain:
        print(explain(settings.explain, settings.load or []))
        return 0

    errors = run_refurb(settings)

    for error in errors:
        print(error)

    return 1 if errors else 0
