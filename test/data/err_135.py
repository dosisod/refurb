# these should match

d = {}

def f1():
    for k, _ in d.items():
        print(k)


def f2():
    for _, v in d.items():
        print(v)


def f3():
    for k, v in d.items():
        # "v" is unused, warn
        print(k)


def f4():
    for k, v in d.items():
        # "k" is unused, warn
        print(v)


def f5():
    (k for k, _ in d.items())
    (v for _, v in d.items())


def f6():
    {k: "" for k, _ in d.items()}
    {v: "" for _, v in d.items()}


# these should not

def f7():
    for k, v in d.items():
        print(k, v)


class Shelf:
    def items(self) -> list[tuple[str, int]]:
        return [("bagels", 123)]

def f8():
    shelf = Shelf()

    for name, count in shelf.items():
        pass
