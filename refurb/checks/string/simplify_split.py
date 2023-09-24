from dataclasses import dataclass

from mypy.nodes import CallExpr, MemberExpr, StrExpr

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    `split(" ")` can be simplified to just `split()`.
    """

    name = "simplify-split"
    code = 179
    msg: str = 'Replace `split(" ")` with `split()`'
    categories = ("string", "readability")


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=MemberExpr(name="split"),
            args=[StrExpr(value=" ")],
        ):
            errors.append(ErrorInfo.from_node(node))
