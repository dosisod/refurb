from dataclasses import dataclass

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    prefix = "XYZ"
    code = 104
    msg: str = "Your message here"


def check(node: int, errors: list[Error]) -> None:
    pass
