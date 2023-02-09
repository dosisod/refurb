# these should match

def f(x):
    match x:
        case bool() as a: pass
        case bytearray() as b: pass
        case bytes() as c: pass
        case dict() as d: pass
        case float() as e: pass
        case frozenset() as f: pass
        case int() as g: pass
        case list() as h: pass
        case set() as i: pass
        case str() as j: pass
        case tuple() as k: pass


# these should not

match 1:
    case int(x): pass
    case float(x) as y: pass
    case str(key=value) as y: pass  # type: ignore
    case 1: pass
    case x: pass
