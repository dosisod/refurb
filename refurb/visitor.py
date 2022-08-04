import importlib
import pkgutil
from collections import defaultdict
from inspect import signature
from typing import Callable, Type

from mypy.nodes import Node, OpExpr, WithStmt
from mypy.traverser import TraverserVisitor

from . import checks
from .error import Error


class RefurbVisitor(TraverserVisitor):
    errors: list[Error]
    checks: defaultdict[Type[Node], list[Callable[[Node, list[Error]], None]]]

    def __init__(self) -> None:
        self.errors = []
        self.checks = defaultdict(list)

        self.load_checks()

    def load_checks(self) -> None:
        for info in pkgutil.walk_packages(checks.__path__, "refurb.checks."):
            if info.ispkg:
                continue

            module = importlib.import_module(info.name)

            if func := getattr(module, "check", None):
                params = list(signature(func).parameters.values())

                self.checks[params[0].annotation].append(func)

    def visit_op_expr(self, o: OpExpr) -> None:
        super().visit_op_expr(o)

        for f in self.checks[OpExpr]:
            f(o, self.errors)

    def visit_with_stmt(self, o: WithStmt) -> None:
        super().visit_with_stmt(o)

        for f in self.checks[WithStmt]:
            f(o, self.errors)
