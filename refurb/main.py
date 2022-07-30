import sys

from mypy.build import build
from mypy.main import process_options
from mypy.nodes import OpExpr
from mypy.traverser import TraverserVisitor

from .checks.pathlib.with_suffix import slice_then_concat
from .error import Error


class RefurbVisitor(TraverserVisitor):
    errors: list[Error]

    def __init__(self) -> None:
        self.errors = []

    def visit_op_expr(self, o: OpExpr) -> None:
        super().visit_op_expr(o)

        slice_then_concat(o, self.errors)


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


if __name__ == "__main__":
    errors = main(sys.argv[1:])

    for error in errors:
        print(error)
