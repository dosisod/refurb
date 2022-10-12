from dataclasses import dataclass

from mypy.nodes import MypyFile

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    enabled = False
    prefix = "XYZ"
    code = 101
    msg: str = "This message is disabled by default"


def check(node: MypyFile, errors: list[Error]) -> None:
    errors.append(ErrorInfo(node.line, node.column))
