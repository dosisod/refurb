from dataclasses import dataclass
from io import StringIO
from typing import Sequence

from mypy.build import build
from mypy.errors import CompileError
from mypy.main import process_options

from .error import Error
from .explain import explain
from .visitor import RefurbVisitor


@dataclass
class Cli:
    files: list[str] | None = None
    explain: int | None = None
    ignore: set[int] | None = None


def parse_error_id(err: str) -> int:
    id = err.replace("FURB", "")

    if id.isdigit():
        return int(id)

    raise ValueError(f'refurb: "{id}" must be in form FURB123 or 123')


def parse_args(args: list[str]) -> Cli:
    if len(args) == 0:
        raise ValueError("refurb: no arguments passed")

    if args[0] == "--explain":
        if len(args) != 2:
            raise ValueError("usage: refurb --explain ID")

        return Cli(explain=parse_error_id(args[1]))

    iargs = iter(args)
    files: list[str] = []
    ignore: set[int] = set()

    for arg in iargs:
        if arg == "--ignore":
            value = next(iargs, None)

            if value is None:
                raise ValueError(f'refurb: missing argument after "{arg}"')

            ignore.add(parse_error_id(value))

        elif arg.startswith("-"):
            raise ValueError(f'refurb: unsupported option "{arg}"')

        else:
            files.append(arg)

    return Cli(files=files, ignore=ignore or None)


def run_refurb(cli: Cli) -> Sequence[Error | str]:
    stderr = StringIO()

    try:
        files, opt = process_options(cli.files or [], stderr=stderr)

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

    errors: list[Error] = []

    for file in files:
        if tree := result.graph[file.module].tree:
            rv = RefurbVisitor(cli.ignore)

            tree.accept(rv)

            for error in rv.errors:
                error.filename = file.path

            errors += rv.errors

    return errors


def main(args: list[str]) -> None:
    try:
        cli = parse_args(args)

    except ValueError as e:
        print(e)
        return

    if cli.explain:
        print(explain(cli.explain))
        return

    errors = run_refurb(cli)

    for error in errors:
        print(error)
