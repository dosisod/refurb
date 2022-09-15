class DummyResource:
    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass

# these will match

def func():
    x = ""

    with DummyResource():
        x = "some value"


x = ""

with DummyResource():
    x = "some value"


# these will not

