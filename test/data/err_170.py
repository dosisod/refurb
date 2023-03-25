import re
from re import search

PATTERN = re.compile("hello( world)?")

# these should match

_ = re.search(PATTERN, "hello world")
_ = re.match(PATTERN, "hello world")
_ = re.fullmatch(PATTERN, "hello world")
_ = re.split(PATTERN, "hello world")
_ = re.split(PATTERN, "hello world", 1)
_ = re.split(PATTERN, "hello world", maxsplit=1)
_ = re.findall(PATTERN, "hello world")
_ = re.finditer(PATTERN, "hello world")
_ = re.sub(PATTERN, "hello world", "goodbye world")
_ = re.sub(PATTERN, "hello world", "goodbye world", 1)
_ = re.sub(PATTERN, "hello world", "goodbye world", count=1)
_ = re.subn(PATTERN, "hello world", "goodbye world")
_ = re.subn(PATTERN, "hello world", "goodbye world", count=1)

_ = search(PATTERN, "hello world")


# these should not

_ = re.search(PATTERN, "hello world", re.IGNORECASE)
_ = re.match(PATTERN, "hello world", re.IGNORECASE)
_ = re.fullmatch(PATTERN, "hello world", re.IGNORECASE)
_ = re.split(PATTERN, "hello world", flags=re.IGNORECASE)
_ = re.split(PATTERN, "hello world", 1, flags=re.IGNORECASE)
_ = re.findall(PATTERN, "hello world", re.IGNORECASE)
_ = re.finditer(PATTERN, "hello world", re.IGNORECASE)
_ = re.sub(PATTERN, "hello world", "goodbye world", flags=re.IGNORECASE)
_ = re.sub(PATTERN, "hello world", "goodbye world", 1, re.IGNORECASE)
_ = re.subn(PATTERN, "hello world", "goodbye world", flags=re.IGNORECASE)
_ = re.subn(PATTERN, "hello world", "goodbye world", 1, flags=re.IGNORECASE)

_ = PATTERN.search("hello world")

_ = re.search("hello world", "hello world")
