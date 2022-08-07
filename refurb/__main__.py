import sys

from refurb.main import main as _main


def main() -> None:
    _main(sys.argv[1:])


if __name__ == "__main__":
    main()
