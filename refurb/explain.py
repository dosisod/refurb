from pathlib import Path
from textwrap import dedent

from refurb.loader import get_error_class, get_modules
from refurb.settings import Settings

from .error import ErrorCode


def explain(settings: Settings) -> str:
    lookup = settings.explain

    for module in get_modules(settings.load):
        error = get_error_class(module)

        if error and ErrorCode.from_error(error) == lookup:
            docstring = error.__doc__ or ""

            if docstring.startswith(f"{error.__name__}("):
                return f'refurb: Explanation for "{lookup}" not found'

            output = ""

            if settings.verbose:
                root = Path(__file__).parent.parent
                file = Path(module.__file__ or "").relative_to(root)

                output += f"Filename: {file}\n\n"

            docstring = dedent(error.__doc__ or "").strip()

            name = error.name or "<name unknown>"
            error_code = ErrorCode.from_error(error)
            categories = " ".join(f"[{x}]" for x in error.categories)

            output += f"{error_code}: {name} {categories}\n\n{docstring}"

            return output

    return f'refurb: Error code "{lookup}" not found'
