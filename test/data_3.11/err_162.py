from datetime import datetime

# these should match

datetime.fromisoformat("2024-02-15T00:00:00.000000Z".replace("Z", "+00:00"))
datetime.fromisoformat("2024-02-15T00:00:00.000000Z".replace("Z", "-00:00"))
datetime.fromisoformat("2024-02-15T00:00:00.000000Z".replace("Z", "+0000"))
datetime.fromisoformat("2024-02-15T00:00:00.000000Z".replace("Z", "-0000"))
datetime.fromisoformat("2024-02-15T00:00:00.000000Z".replace("Z", "+00"))
datetime.fromisoformat("2024-02-15T00:00:00.000000Z".replace("Z", "-00"))

x = "2024-02-15T00:00:00.000000Z"
datetime.fromisoformat(x.replace("Z", "+00:00"))

datetime.fromisoformat("2024-02-15T00:00:00.000000Z"[:-1] + "+00:00")
datetime.fromisoformat("2024-02-15T00:00:00.000000Z".strip("Z") + "+00:00")
datetime.fromisoformat("2024-02-15T00:00:00.000000Z".rstrip("Z") + "+00:00")

class Wrapper:
    s: str

datetime.fromisoformat(Wrapper().s.rstrip("Z") + "+00:00")

def f():
    import datetime as dt
    dt.datetime.fromisoformat("2024-02-15T00:00:00.000000Z".rstrip("Z") + "+00:00")


# these should not

datetime.fromisoformat("2024-02-15T00:00:00.000000Z".replace("XYZ", "+00:00"))
datetime.fromisoformat("2024-02-15T00:00:00.000000Z".replace("Z", "+10:00"))

datetime.fromisoformat("2024-02-15T00:00:00.000000Z"[:1] + "+00:00")
datetime.fromisoformat("2024-02-15T00:00:00.000000Z"[1:1] + "+00:00")
datetime.fromisoformat("2024-02-15T00:00:00.000000Z"[:-1:1] + "+00:00")

class C:
    def replace(self, this: str, that: str) -> str:
        return this + that

c = C()
datetime.fromisoformat(c.replace("Z", "+00:00"))
