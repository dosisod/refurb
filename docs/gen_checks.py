import re
from pathlib import Path
from textwrap import dedent

from refurb.error import ErrorCode
from refurb.loader import get_error_class, get_modules

docs: dict[str, str] = {}

for module in get_modules([]):
    if error := get_error_class(module):
        error_code = ErrorCode.from_error(error)

        header = f"## {error_code}: `{error.name}`"

        categories = " ".join(f"`{cat}`" for cat in error.categories)
        categories = "Categories: " + categories

        body = dedent(error.__doc__ or "").strip()
        body = re.sub(r"```([\s\S]*?)```", r"```python\1```", body)

        docs[str(error_code)] = "\n\n".join([header, categories, body])


with (Path(__file__).parent / "checks.md").open("w+") as f:
    for k, v in sorted(docs.items()):
        f.write("\n")
        f.write(v)
