from pathlib import Path

# these should match

_ = Path("file.txt").name.endswith(".txt")
_ = Path("file.ABC").name.endswith(".ABC")


# these should not

_ = Path("file.txt.gz").name.endswith(".txt.gz")
_ = Path("file").name.endswith("file")
_ = Path("file").name.endswith("")

_ = Path("file").suffix.endswith(".txt")

_ = Path("file").name.startswith("file")
