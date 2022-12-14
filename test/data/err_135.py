# these should match

d = {}

def f1():
    for k, _ in d.items():
        print(k)


def f2():
    for _, v in d.items():
        print(v)


def f3():
    (k for k, _ in d.items())
    (v for _, v in d.items())


def f4():
    {k: "" for k, _ in d.items()}
    {v: "" for _, v in d.items()}


def f5():
    (k for k, v in d.items())  # "v" is unused, warn
    (v for k, v in d.items())  # "k" is unused, warn

    {k: "" for k, v in d.items()}  # "v" is unused, warn
    {v: "" for k, v in d.items()}  # "k" is unused, warn


# these should not

def f6():
    for k, v in d.items():
        print(k, v)


class Shelf:
    def items(self) -> list[tuple[str, int]]:
        return [("bagels", 123)]

def f7():
    shelf = Shelf()

    for name, count in shelf.items():
        pass


def f8():
    k=v=0

    # don't warn because we can't know if "k" or "v" are unused simply by
    # looking at the for block, we need to account for the surrounding context,
    # which is not possible currently.
    for k, v in d.items():
        pass

    print(k, v)

def f9():
    {k: "" for k, v in d.items() if v}
    {v: "" for k, v in d.items() if k}

    (k for k, v in d.items() if v)
    (v for k, v in d.items() if k)
