import pathlib
from pathlib import Path

# these should match

_ = Path().resolve()
_ = Path("").resolve()  # noqa: FURB153
_ = Path(".").resolve()  # noqa: FURB153
_ = pathlib.Path().resolve()


# these should not

_ = Path("some_file").resolve()
_ = Path().resolve(True)
_ = Path().resolve(False)  # noqa: FURB120

p = Path()
_ = p.resolve()
