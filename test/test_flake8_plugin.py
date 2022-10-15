import ast
from pathlib import Path

from refurb.flake8 import Flake8Error, Flake8Refurb


def _check_with_plugin(file: Path) -> set[Flake8Error]:
    """
    Emulate what flake8 would do with this plugin.
    """
    tree = ast.parse(file.read_text())
    plugin = Flake8Refurb(tree=tree, filename=str(file))
    return set(plugin.run())


def test_err_100():
    expected = {
        Flake8Error(
            line=5,
            column=8,
            message="FRB100 Use `Path(x).with_suffix(y)` instead of slice and concat",
            source=Flake8Refurb,
        ),
        Flake8Error(
            line=8,
            column=8,
            message="FRB100 Use `Path(x).with_suffix(y)` instead of slice and concat",
            source=Flake8Refurb,
        ),
        Flake8Error(
            line=13,
            column=4,
            message="FRB123 Replace `str(x)` with `x`",
            source=Flake8Refurb,
        ),
    }
    assert _check_with_plugin(Path("test/data/err_100.py")) == expected
