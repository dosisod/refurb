# these will match

def stmt_then_return():
    pass

    return

def match_trailing_case():
    match 123:
        case 123:
            print("it is 123!")

        case _:
            return

def if_trailing_return():
    if False:
        pass

    else:
        return

def elif_trailing_return():
    if False:
        pass

    elif False:
        pass

    else:
        return

def nested_match():
    match [123]:
        case [x]:
            match x:
                case 123:
                    pass

                case _:
                    return

def with_stmt():
    with open("file"):
        return


def match_without_wildcard():
    match 1:
        case 1:
            return


def match_multiple_bodies():
    match [123]:
        case [_]:
            print("here")

            return

        case []:
            print("there")

            return

        case _:
            return


# these will not

def just_return():
    return

def return_value():
    return 1


def return_none():
    return None

def if_with_non_trailing_node():
    if False:
        pass

    else:
        pass

    pass

def nested_if_with_non_trailing_node():
    if False:
        pass

    else:
        if False:
            pass

        else:
            return

        pass

def nested_match_with_non_trailing_node():
    match [123]:
        case [x]:
            match x:
                case 123:
                    pass

                case _:
                    return

            pass


def match_with_early_return(x):
    match x:
        case [_]:
            return

        case []:
            return
