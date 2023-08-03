# Check Ideas

This is a running list of checks which I (and others) have suggested, and can
be picked up by anyone looking to add new checks to Refurb!

## Pathlib

### Don't use `+` for path traversal, use `/` operator

Bad:

```python
file = "folder" + "/filename"
```

Good:

```python
file = Path("folder") / "filename"
```

## Dict

### Replace `{x[0]: x[1] for x in y}` with `dict(y)`

We will need to make sure that `len(x) == 2`

## Typing

These should be opt-in, since they can be quite noisy.

* Convert `List` -> `list` (python 3.9+)
  - Include `dict`, `set`, `frozenset`, `defaultdict`, etc
  - See `TypeApplication` Mypy node

* Convert `Optional[x]` -> `x | None` (python 3.10+)

* Convert `Union[x, y]` -> `x | y` (python 3.10+)

## Dataclasses

### Replace boilerplate class with dataclasses

This will be opt-in (dataclasses are simpler, but slightly slower).

Bad:

```python
class Person:
    name: str
    age: int

    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age
```

Good:

```python
@dataclass
class Person:
    name: str
    age: int
```

## String

### Use f-string instead of `+`

Disable by default, will be noisy

### Don't use `" ".join(x.capitalize() for x in s.split())`, use `string.capwords(x)`

Notes:

* Check for `" "`, add as optional param to `capwords`
* Allow for `title` as well as `capitalize`

### Simplify f-string Conversions:

The following are only detected if in an f-string:

* `x.center(y, z)` -> `f"{x:z^y}"`
* `x.ljust(y, z)` -> `f"{x:z<y}"`
* `x.rjust(y, z)` -> `f"{x:z>y}"`

For example:

```python
text = "centered"

print(f"[{text.center(20)}]")

# vs

print(f"[{text:^20}]")
```

## Equality/Logic

### Use Comparison Chain

For example, convert `x > 0 and x < 10` into `0 < x < 10`

## Collections

### Counter

Example TBD

### Default dict

Replace instances similar to this:

```python
d = {}
if x in d:
    d[x].append(y)
else:
    d[x] = [y]
```

With this:

```python
d = defaultdict(list)

d[x].append(y)
```

## List

## Built-in methods

See https://docs.python.org/3/library/stdtypes.html

See https://docs.python.org/3/library/io.html

* Use `frozenset` when `set` is never appended to
* Don't roll your own max/min/sum functions, use `max`/`min`/`sum` instead
* `print(f"{x} {y}")` -> `print(x, y)`
* Don't use `_` in expressions
* Use `x ** y` instead of `pow(x, y)`
  * Unless the `mod` param of `pow` is being used
* Don't call `print()` repeatedly, call `print()` once with multi line string
* Don't call `sys.stderr.write("asdf\n")`, use `print("asdf", file=sys.stderr)`

## Enum

### Use `auto()` if all members of enum are explicitly set, and only increment by one

## Itertools

### Use `itertools.product`

Bad:

```python
for x in range(10):
    for y in range(10):
        pass

    # no code here!
```

Good:

```python
for x, y in product(range(10), range(10)):
    pass
```

### Use `itertools.chain`

Bad:

```python
for item in (*list1, *list2, *list3):
    # do something
```

Good:

```python
for item in itertools.chain(list1, list2, list3):
    # do something
```

## Iteration

### Don't use `x = x[::-1]`, use `x.reverse()`
