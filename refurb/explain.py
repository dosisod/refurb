import importlib
import pkgutil
from textwrap import dedent

from . import checks


def explain(id: int) -> str:
    for info in pkgutil.walk_packages(checks.__path__, "refurb.checks."):
        if info.ispkg:
            continue

        module = importlib.import_module(info.name)

        for name in dir(module):
            if name.startswith("Error") and name != "Error":
                err = getattr(module, name)

                if err.code == id:
                    return dedent(err.__doc__).strip()

    return f"Error: Id {id} not found"
