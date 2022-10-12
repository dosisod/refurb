from collections import defaultdict
from typing import Callable

from mypy.nodes import CallExpr, Node
from mypy.traverser import TraverserVisitor

from ..error import Error
from .mapping import METHOD_NODE_MAPPINGS

Check = Callable[[Node, list[Error]], None]
Checks = defaultdict[type[Node], list[Check]]
VisitorMethod = Callable[["RefurbVisitor", Node], None]


def build_visitor(name: str, ty: type[Node], checks: Checks) -> VisitorMethod:
    def inner(self: RefurbVisitor, o: Node) -> None:
        getattr(TraverserVisitor, name)(self, o)

        for check in checks[ty]:
            check(o, self.errors)

    inner.__name__ = name
    inner.__annotations__["o"] = ty
    return inner


class RefurbVisitor(TraverserVisitor):
    errors: list[Error]

    _dont_build = ("visit_call_expr",)

    def __init__(self, checks: defaultdict[type[Node], list[Check]]) -> None:
        self.errors = []
        self.checks = checks

        types = set(self.checks.keys())

        for name, type in METHOD_NODE_MAPPINGS.items():
            if type in types and name not in self._dont_build:
                func = build_visitor(name, type, self.checks)

                setattr(self, name, func.__get__(self))

    def visit_call_expr(self, o: CallExpr) -> None:
        for arg in o.args:
            arg.accept(self)

        o.callee.accept(self)

        for check in self.checks[CallExpr]:
            check(o, self.errors)
