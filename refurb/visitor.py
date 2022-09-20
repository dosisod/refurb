from collections import defaultdict
from typing import Callable, Type

from mypy.nodes import CallExpr, Node
from mypy.traverser import TraverserVisitor

from ._visitor_mappings import MAPPINGS
from .error import Error

Check = Callable[[Node, list[Error]], None]


def build_visitor(
    name: str, ty: Type[Node], checks: defaultdict[Type[Node], list[Check]]
) -> Callable[["RefurbVisitor", Node], None]:
    def inner(self: RefurbVisitor, o: Node) -> None:
        getattr(TraverserVisitor, name)(self, o)

        for check in checks[ty]:
            check(o, self.errors)

    return inner


class RefurbVisitor(TraverserVisitor):
    errors: list[Error]

    _dont_build = ("visit_call_expr",)

    def __init__(self, checks: defaultdict[Type[Node], list[Check]]) -> None:
        self.errors = []
        self.checks = checks

        types = set(self.checks.keys())

        for name, type in MAPPINGS.items():
            if type in types and name not in self._dont_build:
                func = build_visitor(name, type, self.checks)

                setattr(self, name, func.__get__(self))

    def visit_call_expr(self, o: CallExpr) -> None:
        for arg in o.args:
            arg.accept(self)

        o.callee.accept(self)

        for check in self.checks[CallExpr]:
            check(o, self.errors)
