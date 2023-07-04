from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/")
def index(
    # These should match
    a: str = Query(),
    b: str = Query(...),
    c: str | None = Query(None),
    d: str = Query(default=""),
    e = Query(),
    # These should not
    f: str = Query(title=""),
    g: str = Query("", title="")
) -> None:
    pass
