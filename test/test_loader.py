import pytest
from mypy.nodes import CallExpr

from refurb.error import Error
from refurb.loader import extract_function_types, is_valid_error_class


def test_check_must_be_callable() -> None:
    with pytest.raises(TypeError, match="Check function must be callable"):
        list(extract_function_types(1))


def test_check_must_have_valid_number_of_args() -> None:
    def check() -> None:
        pass

    with pytest.raises(TypeError, match="Check function must take 2-3 parameters"):
        list(extract_function_types(check))


def test_invalid_type_union_nodes_are_ignored() -> None:
    def check(node: CallExpr | int, errors: list[Error]) -> None:
        pass

    with pytest.raises(TypeError, match='"int" is not a valid Mypy node type'):
        list(extract_function_types(check))


def test_invalid_node_types_are_ignored() -> None:
    def check(node: int, errors: list[Error]) -> None:
        pass

    with pytest.raises(TypeError, match='"int" is not a valid Mypy node type'):
        list(extract_function_types(check))


def test_invalid_error_types_are_ignored() -> None:
    def check(node: CallExpr, errors: list[int]) -> None:
        pass

    with pytest.raises(TypeError, match=r'"error" param must be of type list\[Error\]'):
        list(extract_function_types(check))


def test_check_with_optional_settings_param() -> None:
    def check(node: CallExpr, errors: list[Error], settings: int) -> None:
        pass

    with pytest.raises(TypeError, match='"settings: int" is not a valid service'):
        list(extract_function_types(check))


def test_error_info_class_must_be_valid() -> None:
    class ErrorInfo:
        pass

    assert not is_valid_error_class(ErrorInfo)
