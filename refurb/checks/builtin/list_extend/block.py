from mypy.nodes import Block

from refurb.error import Error

from .common import check_stmts


def check(node: Block, errors: list[Error]) -> None:
    check_stmts(node.body, errors)
