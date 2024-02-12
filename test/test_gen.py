from pathlib import Path
from unittest.mock import patch

from refurb.gen import folders_needing_init_file


def test_folder_not_in_cwd_is_ignored():
    with patch("pathlib.Path.cwd", lambda: Path("/some/random/path")):
        assert not folders_needing_init_file(Path("./some/path"))


def test_relative_path_works():
    assert folders_needing_init_file(Path("./a/b/c")) == [
        Path.cwd() / "a" / "b" / "c",
        Path.cwd() / "a" / "b",
        Path.cwd() / "a",
    ]


def test_absolute_path_works():
    assert folders_needing_init_file(Path.cwd() / "a" / "b" / "c" / "d") == [
        Path.cwd() / "a" / "b" / "c" / "d",
        Path.cwd() / "a" / "b" / "c",
        Path.cwd() / "a" / "b",
        Path.cwd() / "a",
    ]
