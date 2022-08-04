from mypy.build import build
from mypy.main import process_options

from .error import Error
from .visitor import RefurbVisitor


def main(args: list[str]) -> list[Error]:
    files, opt = process_options(args)

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
