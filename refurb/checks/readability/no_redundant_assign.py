from dataclasses import dataclass

from mypy.nodes import AssignmentStmt, NameExpr

from refurb.checks.common import unmangle_name
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Sometimes when you are debugging (or copy-pasting code) you will end up
    with a variable that is assigning itself to itself. These lines can be
    removed.

    Bad:

    ```
    name = input("What is your name? ")
    name = name
    ```

    Good:

    ```
    name = input("What is your name? ")
    ```
    """

    code = 160
    name = "no-redundant-assignment"
    categories = ("readability",)
    msg: str = "Remove redundant assignment of variable to itself"


def check(node: AssignmentStmt, errors: list[Error]) -> None:
    match node:
        case AssignmentStmt(
            lvalues=[NameExpr(fullname=lhs_name)],
            rvalue=NameExpr(fullname=rhs_name),
        ) if lhs_name and unmangle_name(lhs_name) == unmangle_name(rhs_name):
            errors.append(ErrorInfo.from_node(node))
