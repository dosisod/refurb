import sys

from refurb.main import main

errors = main(sys.argv[1:])

for error in errors:
    print(error)
