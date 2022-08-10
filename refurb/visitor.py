import importlib
import pkgutil
from collections import defaultdict
from inspect import signature
from typing import Callable, Type

from mypy.nodes import (
    CallExpr,
    ForStmt,
    GeneratorExpr,
    Node,
    OpExpr,
    TryStmt,
    WithStmt,
)
from mypy.traverser import TraverserVisitor

from . import checks
from .error import Error


class RefurbVisitor(TraverserVisitor):
    errors: list[Error]
    checks: defaultdict[Type[Node], list[Callable[[Node, list[Error]], None]]]
    ignore: set[int]

    def __init__(self, ignore: set[int] | None = None) -> None:
        self.errors = []
        self.checks = defaultdict(list)
        self.ignore = ignore or set()

        self.load_checks()

    def load_checks(self) -> None:
        for info in pkgutil.walk_packages(checks.__path__, "refurb.checks."):
            if info.ispkg:
                continue

            module = importlib.import_module(info.name)

            if any(
                name.startswith("Error")
                and name != "Error"
                and getattr(module, name).code in self.ignore
                for name in dir(module)
            ):
                continue

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

    def visit_call_expr(self, o: CallExpr) -> None:
        super().visit_call_expr(o)

        for f in self.checks[CallExpr]:
            f(o, self.errors)

    def visit_try_stmt(self, o: TryStmt) -> None:
        super().visit_try_stmt(o)

        for f in self.checks[TryStmt]:
            f(o, self.errors)

    def visit_generator_expr(self, o: GeneratorExpr) -> None:
        super().visit_generator_expr(o)

        for f in self.checks[GeneratorExpr]:
            f(o, self.errors)

    def visit_for_stmt(self, o: ForStmt) -> None:
        super().visit_for_stmt(o)

        for f in self.checks[ForStmt]:
            f(o, self.errors)
