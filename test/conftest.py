from unittest.mock import patch
import pytest

@pytest.fixture(autouse=True)
def fake_tty():
    # Pytest doesnt run in a TTY, so the new TTY detection code is causing a lot of color related
    # tests to fail. This hack makes it so color is always enabled, like it would in a normal TTY.
    with patch("sys.stdout.isatty") as p:
        p.return_value = True
        yield p
