from pathlib import Path
from refurb.main import main


for test in Path("test/data").glob("*.py"):
    errors = main([str(test)])

    expected = test.with_suffix(".txt").read_text()[:-1]
    got = "\n".join([str(error) for error in errors])

    assert got == expected
