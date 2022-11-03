import importlib
import pkgutil
import sys
from collections import defaultdict
from collections.abc import Generator
from importlib.metadata import entry_points
from inspect import signature
from pathlib import Path
from types import ModuleType, UnionType
from typing import cast

from mypy.nodes import Node

from . import checks as checks_module
from .error import Error, ErrorCode
from .settings import Settings
from .types import Check


def get_modules(paths: list[str]) -> Generator[ModuleType, None, None]:
    sys.path.append(str(Path.cwd()))

    plugins = [x.value for x in entry_points(group="refurb.plugins")]
    extra_modules = (importlib.import_module(x) for x in paths + plugins)

    loaded: set[ModuleType] = set()

    for pkg in (checks_module, *extra_modules):
        if pkg in loaded:
            continue

        if not hasattr(pkg, "__path__"):
            module = importlib.import_module(pkg.__name__)

            if module not in loaded:
                loaded.add(module)
                yield module

            continue

        for info in pkgutil.walk_packages(pkg.__path__, f"{pkg.__name__}."):
            if info.ispkg:
                continue

            module = importlib.import_module(info.name)

            if module not in loaded:
                loaded.add(module)
                yield module

        loaded.add(pkg)


def get_error_class(module: ModuleType) -> type[Error] | None:
    for name in dir(module):
        if name.startswith("Error") and name not in ("Error", "ErrorCode"):
            return cast(type[Error], getattr(module, name))

    return None


def should_skip_loading_check(settings: Settings, error: type[Error]) -> bool:
    error_code = ErrorCode.from_error(error)

    error_is_disabled = settings.disable_all or not error.enabled
    should_enable = settings.enable_all or error_code in settings.enable

    in_disable_list = error_code in (settings.ignore | settings.disable)

    return (error_is_disabled and not should_enable) or in_disable_list


def load_checks(settings: Settings) -> defaultdict[type[Node], list[Check]]:
    found: defaultdict[type[Node], list[Check]] = defaultdict(list)

    for module in get_modules(settings.load):
        error = get_error_class(module)

        if not error or should_skip_loading_check(settings, error):
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
