from datetime import datetime

# these should match

datetime.fromisoformat("".replace("Z", "+00:00"))
datetime.fromisoformat("".replace("Z", "-00:00"))
datetime.fromisoformat("".replace("Z", "+0000"))
datetime.fromisoformat("".replace("Z", "-0000"))
datetime.fromisoformat("".replace("Z", "+00"))
datetime.fromisoformat("".replace("Z", "-00"))

x = ""
datetime.fromisoformat(x.replace("Z", "+00:00"))

datetime.fromisoformat(""[:-1] + "+00:00")
datetime.fromisoformat("".strip("Z") + "+00:00")
datetime.fromisoformat("".rstrip("Z") + "+00:00")


# these should not

datetime.fromisoformat("".replace("XYZ", "+00:00"))
datetime.fromisoformat("".replace("Z", "+10:00"))

datetime.fromisoformat(""[:1] + "+00:00")
datetime.fromisoformat(""[1:1] + "+00:00")
datetime.fromisoformat(""[:-1:1] + "+00:00")

class C:
    def replace(self, this: str, that: str) -> str:
        return this + that

c = C()
datetime.fromisoformat(c.replace("Z", "+00:00"))
