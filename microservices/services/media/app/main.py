from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="/app/static"), name="static")

@app.get("/health")
def health():
    return {"status": "ok", "service": "media"}


