import itertools
import typing
from collections.abc import Iterable

import pytest
from mypy.nodes import Node

from refurb.settings import Settings
from refurb.types import Checks
from refurb.visitor import METHOD_NODE_MAPPINGS, RefurbVisitor
from refurb.visitor.mapping import VisitorNodeTypeMap

from .mypy_visitor import get_mypy_visitor_mapping


@pytest.fixture
def dummy_visitor() -> RefurbVisitor:
    """
    This fixture provides a RefurbVisitor instance with a visit method for each
    possible node, but no checks to run.

    This forces method generation but calling the methods does nothing.
    """
    checks = Checks(list, {ty: [] for ty in METHOD_NODE_MAPPINGS.values()})
    return RefurbVisitor(checks, Settings())


def get_visit_methods(
    visitor: RefurbVisitor,
) -> Iterable[tuple[str, type[Node]]]:
    """
    Find visitor methods in the instance's __dict__ (those that have been
    generated in __init__) and in the class' __dict__ (the ones that are
    overridden directly in the class).

    Not using inspect.getmembers because that goes too deep into the parents
    and that would deafeat the purpose of this, which is testing that the
    methods are defined in the RefurbVisitor.
    """
    method_sources = itertools.chain(
        visitor.__dict__.items(), visitor.__class__.__dict__.items()
    )
    for method_name, method in method_sources:
        if callable(method) and method_name.startswith("visit_"):
            yield method_name, method


def test_visitor_generation(dummy_visitor: RefurbVisitor) -> None:
    """
    Ensure the visitor creates all expected methods with the right types (The
    ones listed in refurb.visitor.METHOD_NODE_MAPPINGS).
    """

    visitor_mappings: VisitorNodeTypeMap = {}
    for method_name, method in get_visit_methods(dummy_visitor):
        method_types = typing.get_type_hints(method)
        assert "o" in method_types, f"No 'o' parameter in method {method_name}"
        node_type = method_types["o"]
        visitor_mappings[method_name] = node_type

    assert visitor_mappings == METHOD_NODE_MAPPINGS


def test_mypy_consistence() -> None:
    """
    Ensure the visitor method name to node type mappings used in refurb are
    in sync with the ones of mypy.

    This is meant as a failsafe, especially when the mypy dependency is
    upgraded.

    If this fails, review the mappings in refurb.visitor.METHOD_NODE_MAPPINGS.
    """

    mypy_visitor_mapping = get_mypy_visitor_mapping()
    assert METHOD_NODE_MAPPINGS == mypy_visitor_mapping
