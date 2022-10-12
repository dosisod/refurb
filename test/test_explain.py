from refurb.error import ErrorCode
from refurb.explain import explain


def test_get_check_explaination_by_id() -> None:
    assert "error" not in explain(ErrorCode(100)).lower()


def test_error_if_check_doesnt_exist() -> None:
    msg = explain(ErrorCode(999))

    assert msg == 'refurb: Error code "FURB999" not found'


def test_check_with_no_docstring_gives_error() -> None:
    msg = explain(ErrorCode(100, "XYZ"), ["test.custom_checks"])

    assert msg == 'refurb: Explaination for "XYZ100" not found'
