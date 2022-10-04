import importlib
import pkgutil
import sys
from collections import defaultdict
from collections.abc import Generator
from importlib.metadata import entry_points
from inspect import signature
from pathlib import Path
from types import ModuleType, UnionType
from typing import Callable, Type, cast

from mypy.nodes import Node

from . import checks as checks_module
from .error import Error, ErrorCode
from .settings import Settings

Check = Callable[[Node, list[Error]], None]


def get_modules(paths: list[str]) -> Generator[ModuleType, None, None]:
    sys.path.append(str(Path.cwd()))

    plugins = [x.value for x in entry_points(group="refurb.plugins")]

    extra_modules = (__import__(x) for x in paths + plugins)

    for pkg in (checks_module, *extra_modules):
        for info in pkgutil.walk_packages(pkg.__path__, f"{pkg.__name__}."):
            if info.ispkg:
                continue

            yield importlib.import_module(info.name)


def get_error_class(module: ModuleType) -> type[Error] | None:
    for name in dir(module):
        if name.startswith("Error") and name not in ("Error", "ErrorCode"):
            return cast(type[Error], getattr(module, name))

    return None


def load_checks(settings: Settings) -> defaultdict[Type[Node], list[Check]]:
    found: defaultdict[Type[Node], list[Check]] = defaultdict(list)
    ignore = settings.ignore or set()
    paths = settings.load or []
    enabled = settings.enable or set()

    for module in get_modules(paths):
        error = get_error_class(module)
        if not error:
            continue

        error_code = ErrorCode.from_error(error)

        is_enabled = error.enabled or error_code in enabled

        if not is_enabled or error_code in ignore:
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
