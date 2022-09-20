import importlib
import pkgutil
import sys
from collections import defaultdict
from inspect import signature
from pathlib import Path
from types import UnionType
from typing import Callable, Type

from mypy.nodes import Node

from . import checks as checks_module
from .error import Error

Check = Callable[[Node, list[Error]], None]


def load_checks(
    ignore: set[int], load: list[str]
) -> defaultdict[Type[Node], list[Check]]:
    found: defaultdict[Type[Node], list[Check]] = defaultdict(list)

    sys.path.append(str(Path.cwd()))

    extra = (__import__(x) for x in load)

    for pkg in (checks_module, *extra):
        for info in pkgutil.walk_packages(pkg.__path__, f"{pkg.__name__}."):
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
