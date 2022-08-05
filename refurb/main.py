from dataclasses import dataclass

from mypy.build import build
from mypy.main import process_options

from .error import Error
from .explain import explain
from .visitor import RefurbVisitor


@dataclass
class Cli:
    files: list[str] | None = None
    explain: int | None = None


def parse_args(args: list[str]) -> Cli:
    if args[0] == "--explain":
        if len(args) != 2:
            raise ValueError("usage: refurb --explain ID")

        id = args[1].replace("FURB", "")

        if not id.isdigit():
            raise ValueError(f'Error: "{id}" must be in form FURB123 or 123')

        return Cli(explain=int(id))

    return Cli(files=args)


def run_refurb(filenames: list[str]) -> list[Error]:
    files, opt = process_options(filenames)

    opt.incremental = True
    opt.fine_grained_incremental = True
    opt.cache_fine_grained = True

    result = build(files, options=opt)

    errors: list[Error] = []

    for file in files:
        if tree := result.graph[file.module].tree:
            rv = RefurbVisitor()

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

    errors = run_refurb(cli.files or [])

    for error in errors:
        print(error)
