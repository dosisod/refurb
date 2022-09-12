# these will match

def is_even(x):
    if x % 2 == 0:
        return True

    else:
        return False


def is_even_again(x):
    match x % 2:
        case 0:
            return True

        case _:
            return False

def nested(x):
    match x % 2:
        case 0:
            return True

        case _:
            match x % 3:
                case 0:
                    return True

                case _:
                    return False


# these will not

def func(x):
    if x == 1:
        return True

    else:
        pass

        return False

def func2(x):
    match x % 2:
        case 0:
            return True

        case _:
            pass

            return False

def func3(x):
    match x % 2:
        case 0:
            return True

    return False

def func4(x):
    if x == 1:
        return True

    return False

def func5():
    return False

def func6(x):
    match x:
        case 1:
            return 1

        case 2:
            return 2
