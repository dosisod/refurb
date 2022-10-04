import pytest
import mypy.patterns
import mypy.nodes

from refurb.visitor import VISITOR_NAME_TO_NODE_TYPE_MAPPING

NODE_SOURCES = {
    mypy.nodes.__name__: mypy.nodes,
    mypy.patterns.__name__: mypy.patterns,
}

# Most visitor names to node type name mappings can be inferred
# programmatically by converting the node type to snake_case, but there are
# some exceptions, captured here.
IRREGULAR_MAPPINGS = {
    "visit_func": mypy.nodes.FuncItem,
    "visit_ellipsis": mypy.nodes.EllipsisExpr,
}


def regular_visitor_to_node_pairs():
    """
    Produce all mappings, except the irregular ones.

    To be used as test parameters.
    """
    for visitor_name, node in VISITOR_NAME_TO_NODE_TYPE_MAPPING.items():
        if visitor_name not in IRREGULAR_MAPPINGS:
            yield visitor_name, node


@pytest.mark.parametrize(
    "visitor_name, node_type", regular_visitor_to_node_pairs()
)
def test_visitor_to_node_correspondence(visitor_name, node_type):
    """
    Ensures the mapping between visitor methods and node types looks okayish
    by their names.
    """
    visitor_stem = visitor_name.replace("visit_", "").replace("_", "").lower()
    type_stem = node_type.__name__.split(".")[-1].lower()
    assert visitor_stem == type_stem


@pytest.mark.parametrize("visitor_name, node_type", IRREGULAR_MAPPINGS.items())
def test_special_named_mappings(visitor_name, node_type):
    """
    Ensure that irregular mappings were created as expected
    """
    assert VISITOR_NAME_TO_NODE_TYPE_MAPPING[visitor_name] == node_type


@pytest.mark.parametrize(
    "node_type",
    VISITOR_NAME_TO_NODE_TYPE_MAPPING.values(),
    ids=lambda n: n.__name__,
)
def test_node_type_origin(node_type):
    """
    Test that the node type objects stored in the mapping are the ones coming
    from the currently imported mypy modules.

    This is done to ensure that the pure python versions used for loading did
    not leak out.
    """
    assert node_type.__module__ in NODE_SOURCES
    expected_node = getattr(
        NODE_SOURCES[node_type.__module__], node_type.__name__
    )
    assert node_type == expected_node
