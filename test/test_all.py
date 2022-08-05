from pathlib import Path

from refurb.main import run_refurb

for test in Path("test/data").glob("*.py"):
    errors = run_refurb([str(test)])

    expected = test.with_suffix(".txt").read_text()[:-1]
    got = "\n".join([str(error) for error in errors])

    assert got == expected
