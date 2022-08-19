from mypy.nodes import MypyFile

from refurb.error import Error

from .common import check_stmts


def check(node: MypyFile, errors: list[Error]) -> None:
    check_stmts(node.defs, errors)
