from refurb.explain import explain


def test_get_check_explaination_by_id() -> None:
    assert not explain(100).startswith("Error:")


def test_error_if_check_doesnt_exist() -> None:
    assert explain(-1).startswith("Error:")
