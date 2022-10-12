from pathlib import Path

import pytest

pytest_plugins = ["test.mypy_visitor"]


@pytest.fixture(scope="session")
def test_data_path() -> Path:
    data_path = Path(__file__).parent / "data"
    assert data_path.exists()
    assert data_path.is_dir()
    return data_path
