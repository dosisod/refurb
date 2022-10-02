"""
This module provides a mapping between a method name in a Visitor or Mypy's
ASTs and the type of the Node it is meant to visit.

The purpose of this is to enable the dynamic creation of visitors to the AST.

This information is surprisingly hard to obtain programmatically. The approach
here is to explore all the methods of an existing Visitor class in Mypy:
mypy.traverser.TraverserVisitor and obtain the type annotation for their first
(non-self) parameter.

This is further complicated by the fact that Mypy loads by default as compiled
code, and typing information for methods if thus not available.

Here we use a trick found here on Stack Overflow
https://stackoverflow.com/a/68685189/ to create a context manager that
temporarily forces a preference for pure python modules when importing.

So roughly, we do this:

1. Import the mypy things we need
2. Capture the globals (so that we can resolve the strigified type annotations
   to the correct types)
3. Clear the mypy imported modules
4. Import them again with their pure python versions
5. Inspect the Visitor to get the type names, but resolve them using the
   captured globals (from the native versions)
6. Restore the native mypy implementations

"""
import inspect
import sys
import typing
from contextlib import contextmanager
from dataclasses import dataclass
from importlib.abc import Finder
from importlib.machinery import FileFinder
from types import FunctionType
from typing import Callable, Any
import mypy
import mypy.traverser

VISITOR_NAME_TO_NODE_TYPE_MAPPING = dict()


@contextmanager
def prefer_pure_python_imports():
    """
    During the scope of this context manager, all imports will be done using
    pure python versions when available.

    Credit to this answer on SO: https://stackoverflow.com/a/68685189/
    """

    @dataclass
    class PreferPureLoaderHook:
        orig_hook: Callable[[str], Finder]

        def __call__(self, path: str) -> Finder:
            finder = self.orig_hook(path)
            if isinstance(finder, FileFinder):
                # Move pure python file loaders to the front
                finder._loaders.sort(
                    key=lambda pair: 0 if pair[0] in (".py", ".pyc") else 1
                )  # type: ignore

            return finder

    sys.path_hooks = [PreferPureLoaderHook(h) for h in sys.path_hooks]
    sys.path_importer_cache.clear()

    yield

    # Restore the previous behaviour
    assert all(isinstance(h, PreferPureLoaderHook) for h in sys.path_hooks)
    sys.path_hooks = [h.orig_hook for h in sys.path_hooks]
    sys.path_importer_cache.clear()


@contextmanager
def pure_python_mypy():
    """
    Inside this context, all mypy related imports are done with the pure python
    versions.

    Any existing mypy module that was imported before needs to be reimported
    before use within the context.

    Upon exiting, the previous implementations are restored.
    """

    def loaded_mypy_modules():
        """Covenient block to get names of imported mypy modules"""
        for mod_name in sys.modules:
            if mod_name == "mypy" or mod_name.startswith("mypy."):
                yield mod_name

    # First, backup all imported mypy modules and remove them from sys.modules,
    # so they will not be found in resolution
    saved_mypy = dict()
    for mod_name in list(loaded_mypy_modules()):
        saved_mypy[mod_name] = sys.modules[mod_name]
        del sys.modules[mod_name]

    with prefer_pure_python_imports():
        # After the modules are clean, ensure the newly imported mypy modules
        # are their pure python versions.
        # - Pure python: methods are FunctionType
        # - Native: methods are MethodDescriptorType
        from mypy.traverser import TraverserVisitor

        if type(TraverserVisitor.visit_var) != FunctionType:
            raise ImportError(
                "Could not load the pure python implementation of Mypy"
            )

        # Give back control
        yield

    # We're back and this is where we do cleanup. We'll remove all imported
    # mypy modules (pure python) and restore the previously backed-up ones
    # (allegedly native implementations)
    for mod_name in list(loaded_mypy_modules()):
        del sys.modules[mod_name]

    for mod_name, module in saved_mypy.items():
        sys.modules[mod_name] = module


def _get_class_globals(clazz: type, localns: dict[str, Any]) -> dict[str, Any]:
    """
    Get the globals namespace for the full class hierarchy that starts in
    clazz.

    This follows the recommendation of PEP-563 to resolve stringified type
    annotations at runtime.
    """
    all_globals = localns.copy()
    all_globals.update(localns)
    for base in inspect.getmro(clazz):
        all_globals.update(vars(sys.modules[base.__module__]))
    return all_globals


def _make_mappings(globalns: dict[str, Any]) -> dict[str, "mypy.nodes.Node"]:
    """
    Generate a mapping between the name of a visitor method in TraverserVisitor
    and the type of its first (non-self) parameter.
    """
    visitor_method_map = dict()
    from mypy.traverser import TraverserVisitor

    methods = inspect.getmembers(
        TraverserVisitor,
        lambda o: inspect.isfunction(o) and o.__name__.startswith("visit_"),
    )

    for method_name, method in methods:
        method_params = list(inspect.signature(method).parameters.values())
        param_name = method_params[1].name
        method_types = typing.get_type_hints(method, globalns=globalns)
        visitor_method_map[method_name] = method_types[param_name]
    return visitor_method_map


# Capture the global namespace of the hierarchy of TraverserVisitor before we
# replace it with a short-lived pure-python version inside the context manager
# below.
_globals = _get_class_globals(mypy.traverser.TraverserVisitor, locals())

# Resolve the mappings using the pure-python version of mypy (necessary to
# obtain method signature type info) but then ensure the types are resolved to
# their native counterparts (by passing the previously captured global
# namespace)
with pure_python_mypy():
    VISITOR_NAME_TO_NODE_TYPE_MAPPING |= _make_mappings(globalns=_globals)
