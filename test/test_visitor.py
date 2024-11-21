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
    Find visitor methods in the instance (those that have been generated in
    __init__) and in the class' __dict__ (the ones that are overridden
    directly in the class).

    Not using inspect.getmembers because that goes too deep into the parents
    and that would deafeat the purpose of this, which is testing that the
    methods are defined in the RefurbVisitor.
    """
    method_sources = itertools.chain(
        [
            (method_name, getattr(visitor, method_name))
            for method_name in dir(visitor)
            if hasattr(visitor, method_name)
        ],
        visitor.__class__.__dict__.items(),
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

    # Remove the TypeAliasStmt node if it exists. This is a new node added to Mypy,
    # which means we need to be able to support it in both old and new versions of Mypy.
    # Since Refurb doesn't have any checks that use this node type we can safely ignore
    # it for now until we choose to add support for it.
    mypy_visitor_mapping.pop("visit_type_alias_stmt")

    assert mypy_visitor_mapping == METHOD_NODE_MAPPINGS
