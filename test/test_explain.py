from refurb.error import ErrorCode
from refurb.explain import explain


def test_get_check_explaination_by_id() -> None:
    assert "error" not in explain(ErrorCode(100)).lower()


def test_error_if_check_doesnt_exist() -> None:
    assert explain(ErrorCode(999)) == 'refurb: Error code "FURB999" not found'
