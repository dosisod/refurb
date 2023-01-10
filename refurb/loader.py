import importlib
import pkgutil
import sys
from collections import defaultdict
from collections.abc import Generator
from importlib.metadata import entry_points
from inspect import getsourcefile, getsourcelines, signature
from pathlib import Path
from types import GenericAlias, ModuleType, UnionType
from typing import Any, TypeGuard

from mypy.nodes import Node

from refurb.visitor.mapping import METHOD_NODE_MAPPINGS

from . import checks as checks_module
from .error import Error, ErrorCategory, ErrorCode
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


def is_valid_error_class(obj: Any) -> TypeGuard[type[Error]]:  # type: ignore
    if not hasattr(obj, "__name__"):
        return False

    name = obj.__name__
    ignored_names = ("Error", "ErrorCode", "ErrorCategory")

    return (
        name.startswith("Error")
        and name not in ignored_names
        and issubclass(obj, Error)
    )


def get_error_class(module: ModuleType) -> type[Error] | None:
    for name in dir(module):
        if name.startswith("Error") and name not in ("Error", "ErrorCode"):
            error = getattr(module, name)

            if is_valid_error_class(error):
                return error

    return None


def should_load_check(settings: Settings, error: type[Error]) -> bool:
    error_code = ErrorCode.from_error(error)

    if error_code in settings.enable:
        return True

    if error_code in (settings.disable | settings.ignore):
        return False

    categories = {ErrorCategory(cat) for cat in error.categories}

    if settings.enable & categories:
        return True

    if settings.disable & categories or settings.disable_all:
        return False

    return error.enabled or settings.enable_all


VALID_NODE_TYPES = set(METHOD_NODE_MAPPINGS.values())
VALID_OPTIONAL_ARGS = (("settings", Settings),)


def type_error_with_line_info(  # type: ignore
    func: Any, msg: str
) -> TypeError:
    filename = getsourcefile(func)
    line = getsourcelines(func)[1]

    if not filename:
        return TypeError(msg)  # pragma: no cover

    return TypeError(f"{filename}:{line}: {msg}")


def extract_function_types(  # type: ignore
    func: Any,
) -> Generator[type[Node], None, None]:
    if not callable(func):
        raise TypeError("Check function must be callable")

    params = list(signature(func).parameters.values())

    if len(params) not in (2, 3):
        raise type_error_with_line_info(
            func, "Check function must take 2-3 parameters"
        )

    node_param = params[0].annotation
    error_param = params[1].annotation
    optional_params = params[2:]

    if not (
        type(error_param) == GenericAlias
        and error_param.__origin__ == list
        and error_param.__args__[0] == Error
    ):
        raise type_error_with_line_info(
            func, '"error" param must be of type list[Error]'
        )

    for param in optional_params:
        if (param.name, param.annotation) not in VALID_OPTIONAL_ARGS:
            raise type_error_with_line_info(
                func,
                f'"{param.name}: {param.annotation.__name__}" is not a valid service',  # noqa: E501
            )

    match node_param:
        case UnionType() as types:
            for ty in types.__args__:
                if ty not in VALID_NODE_TYPES:
                    raise type_error_with_line_info(
                        func,
                        f'"{ty.__name__}" is not a valid Mypy node type',
                    )

                yield ty

        case ty if ty in VALID_NODE_TYPES:
            yield ty

        case _:
            raise type_error_with_line_info(
                func,
                f'"{ty.__name__}" is not a valid Mypy node type',
            )


def load_checks(settings: Settings) -> defaultdict[type[Node], list[Check]]:
    found: defaultdict[type[Node], list[Check]] = defaultdict(list)

    for module in get_modules(settings.load):
        error = get_error_class(module)

        if error and should_load_check(settings, error):
            if func := getattr(module, "check", None):
                for ty in extract_function_types(func):
                    found[ty].append(func)

    return found
