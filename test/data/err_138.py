# these should match

def f1():
    arr = []

    for num in (1, 2, 3):
        arr.append(num)


def f2():
    arr = []

    for num in (1, 2, 3):
        arr.append(num + 1)


def f3():
    arr = []

    for num in (1, 2, 3):
        if num % 2:
            arr.append(num)


nums = []

for num in (1, 2, 3):
    if num % 2:
        nums.append(num)


# should not match

def f4():
    arr = []

    for num in (1, 2, 3):
        pass

        arr.append(num)


def f5():
    arr = []

    for num in (1, 2, 3):
        arr.pop(num)


def f6():
    # Although this should be caught, the general case for this is a bit harder
    # then expected.
    arr2 = []
    arr = []

    for num in (1, 2, 3):
        arr2.append(num)


def f7():
    arr = []

    for num in (1, 2, 3):
        if x := num + 1:
            arr.append(x)


def f8():
    s = "abc"

    for num in (1, 2, 3):
        s.append(num)


def f9():
    arr = []

    pass

    for num in (1, 2, 3):
        arr.append(num)


def f10():
    arr = [1, 2, 3]

    for num in (1, 2, 3):
        arr.append(num)


def f11():
    arr = []

    for num in (1, 2, 3):
        if num not in arr:
            arr.append(arr)


def f12():
    arr = []

    for num in (1, 2, 3):
        arr.append(arr)
