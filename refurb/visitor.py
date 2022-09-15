import importlib
import pkgutil
from collections import defaultdict
from inspect import signature
from types import UnionType
from typing import Callable, Type

from mypy.nodes import Node
from mypy.traverser import TraverserVisitor

from . import checks
from ._visitor_mappings import MAPPINGS
from .error import Error

Check = Callable[[Node, list[Error]], None]


def load_checks(ignore: set[int]) -> defaultdict[Type[Node], list[Check]]:
    found: defaultdict[Type[Node], list[Check]] = defaultdict(list)

    for info in pkgutil.walk_packages(checks.__path__, "refurb.checks."):
        if info.ispkg:
            continue

        module = importlib.import_module(info.name)

        if any(
            name.startswith("Error")
            and name != "Error"
            and getattr(module, name).code in ignore
            for name in dir(module)
        ):
            continue

        if func := getattr(module, "check", None):
            params = list(signature(func).parameters.values())

            match params[0].annotation:
                case UnionType() as types:
                    for ty in types.__args__:
                        found[ty].append(func)

                case ty:
                    found[ty].append(func)

    return found


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

    def __init__(self, ignore: set[int] | None = None) -> None:
        self.errors = []

        checks = load_checks(ignore or set())
        types = set(checks.keys())

        for name, type in MAPPINGS.items():
            if type in types:
                func = build_visitor(name, type, checks)

                setattr(self, name, func.__get__(self))
