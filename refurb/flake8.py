"""
This is a Flake8 plugin that runs Refurb on each checked file.
"""
import ast
import importlib.metadata
from dataclasses import dataclass
from typing import ClassVar, Generator, NamedTuple, cast

from .error import Error as RefurbError
from .main import run_refurb
from .settings import Settings, load_settings

PREFIX = "FRB"


class Flake8Error(NamedTuple):
    """
    Flake 8 plugins need to deliver tuples. This is a named tuple for
    readability.
    """

    line: int
    column: int
    message: str
    source: type  # This is not used in Flake8, but it is still required


@dataclass
class Flake8Refurb:
    """
    A Flake8 plugin that runs Refurb on the checked files.
    """

    # Name of the plugin
    name: ClassVar[str] = "flake8-refurb"

    # Version of the plugin: same as Refurb's
    version: ClassVar[str] = importlib.metadata.version("refurb")

    # This plugin is off by default and needs to be enabled with
    # "--enable-extensions FRB" passed to flake8
    off_by_default: ClassVar[bool] = True

    # Refurb settings (only those read from config files)
    settings: ClassVar[Settings] = load_settings([])

    # This is a tree-type plugin. It gets called once per file and gets the
    # parsed AST as parameter for init. This needs to be called tree.
    # This tree is not used in the plugin, but it is the only way to tell
    # flake8 to run this once per file.
    tree: ast.AST

    # The filename that is being checked gets passed when this is instantiated
    # once per file.
    filename: str

    def run(self) -> Generator[Flake8Error, None, None]:
        """
        Flake8's entry point, this gets called once per file and needs to yield
        all errors found on that file.
        """
        settings = Settings.merge(
            self.settings,
            Settings(files=[self.filename], exclude_mypy_errors=True),
        )
        for refurb_error in run_refurb(settings=settings):
            refurb_error = cast(RefurbError, refurb_error)
            yield Flake8Error(
                line=refurb_error.line,
                column=refurb_error.column,
                message=f"{PREFIX}{refurb_error.code} {refurb_error.msg}",
                source=type(self),
            )
