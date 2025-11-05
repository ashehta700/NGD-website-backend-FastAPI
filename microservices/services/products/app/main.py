from fastapi import FastAPI
from .router import router as products_router

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok", "service": "products"}

app.include_router(products_router)


