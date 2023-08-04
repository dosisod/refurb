from refurb.error import ErrorCode
from refurb.explain import explain


def test_get_check_explanation_by_id() -> None:
    explanation = explain(ErrorCode(100))

    from refurb.checks.pathlib.with_suffix import ErrorInfo as furb100

    assert "error" not in explanation.lower()
    assert furb100.name
    assert furb100.name in explanation
    assert "FURB100" in explanation
    assert all(cat in explanation for cat in furb100.categories)


def test_error_if_check_doesnt_exist() -> None:
    msg = explain(ErrorCode(999))

    assert msg == 'refurb: Error code "FURB999" not found'


def test_check_with_no_docstring_gives_error() -> None:
    msg = explain(ErrorCode(102, "XYZ"), ["test.custom_checks"])

    assert msg == 'refurb: Explanation for "XYZ102" not found'
