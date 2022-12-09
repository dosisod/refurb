from pathlib import Path

# these will match

a = str(Path("file.txt"))[:4] + ".pdf"

p = Path("file.txt")
b = str(p)[:4] + ".pdf"


# these will not

x = str("file.txt")[:4] + ".pdf"  # noqa: FURB123
