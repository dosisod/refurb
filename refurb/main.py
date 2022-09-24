from io import StringIO
from typing import Sequence

from mypy.build import build
from mypy.errors import CompileError
from mypy.main import process_options

from .error import Error
from .explain import explain
from .gen import main as generate
from .loader import load_checks
from .settings import Settings, load_settings
from .visitor import RefurbVisitor


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

    return sorted(errors, key=sort_errors)


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
