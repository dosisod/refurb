from collections import defaultdict
from collections.abc import Callable

from mypy.nodes import CallExpr, Node

from refurb.error import Error
from refurb.settings import Settings
from refurb.types import Check, Checks
from refurb.visitor import TraverserVisitor

from .mapping import METHOD_NODE_MAPPINGS

VisitorMethod = Callable[["RefurbVisitor", Node], None]


def build_visitor(name: str, ty: type[Node], checks: Checks) -> VisitorMethod:
    def inner(self: RefurbVisitor, o: Node) -> None:
        for check in checks[ty]:
            self.run_check(o, check)

        getattr(TraverserVisitor, name)(self, o)

    inner.__name__ = name
    inner.__annotations__["o"] = ty
    return inner


class RefurbVisitor(TraverserVisitor):
    errors: list[Error]
    settings: Settings

    _dont_build = ("visit_call_expr",)

    def __init__(self, checks: defaultdict[type[Node], list[Check]], settings: Settings) -> None:
        self.errors = []
        self.checks = checks
        self.settings = settings

        types = set(self.checks.keys())

        for name, type in METHOD_NODE_MAPPINGS.items():
            if type in types and name not in self._dont_build:
                func = build_visitor(name, type, self.checks)

                setattr(self, name, func.__get__(self))

    def visit_call_expr(self, o: CallExpr) -> None:
        for check in self.checks[CallExpr]:
            self.run_check(o, check)

        for arg in o.args:
            self.accept(arg)

        self.accept(o.callee)

    def run_check(self, node: Node, check: Check) -> None:
        # Hack: use the type annotations to check if the function takes 2 or
        # 3 arguments. There is an extra field for return types, hence why we
        # use 4.

        if len(check.__annotations__) == 4:
            check(node, self.errors, self.settings)  # type: ignore

        else:
            check(node, self.errors)  # type: ignore
