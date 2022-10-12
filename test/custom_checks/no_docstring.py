from dataclasses import dataclass

from mypy.nodes import EllipsisExpr

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    prefix = "XYZ"
    code = 102
    msg: str = "Your message here"


def check(node: EllipsisExpr, errors: list[Error]) -> None:
    match node:
        case EllipsisExpr():
            errors.append(ErrorInfo(node.line, node.column))
