from dataclasses import dataclass

from mypy.nodes import CallExpr

from refurb.error import Error


@dataclass
class ErrorDisallowCall(Error):
    """
    This check will simply emit an error whenever a `CallExpr` node is hit
    """

    prefix = "XYZ"
    code = 100
    msg: str = "Your message here"


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr():
            errors.append(ErrorDisallowCall(node.line, node.column))
