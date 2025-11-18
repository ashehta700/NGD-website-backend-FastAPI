from fastapi import FastAPI, Request, HTTPException
from app.routers import roles_features,search,auth,users,visitors,projects,news,logos,faq,statistics,products,survey,manual_guide,project_details,requests,admin,videos ,contact_us ,chatbot,metadata,dashboard
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from app.utils.response import error_response
from fastapi.middleware.cors import CORSMiddleware
import os
from app.utils.paths import STATIC_ROOT
# for caching on memory
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend


    
app = FastAPI()



# for cahcing on memory
@app.on_event("startup")
async def on_startup():
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    
    
# Ensure external static directory exists and mount it
os.makedirs(STATIC_ROOT, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_ROOT), name="static")



API_PREFIX = "/api"

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(search.router, prefix=API_PREFIX)
app.include_router(users.router, prefix=API_PREFIX)
app.include_router(roles_features.router, prefix=API_PREFIX)
app.include_router(visitors.router, prefix=API_PREFIX)
app.include_router(projects.router, prefix=API_PREFIX)
app.include_router(news.router, prefix=API_PREFIX)
app.include_router(logos.router, prefix=API_PREFIX)
app.include_router(faq.router, prefix=API_PREFIX)
app.include_router(statistics.router, prefix=API_PREFIX)
app.include_router(products.router, prefix=API_PREFIX)
app.include_router(survey.router, prefix=API_PREFIX)
app.include_router(manual_guide.router, prefix=API_PREFIX)
app.include_router(project_details.router, prefix=API_PREFIX)
app.include_router(requests.router, prefix=API_PREFIX)
app.include_router(admin.router, prefix=API_PREFIX)
app.include_router(videos.router, prefix=API_PREFIX)
app.include_router(contact_us.router, prefix=API_PREFIX)
app.include_router(chatbot.router, prefix=API_PREFIX)
app.include_router(metadata.router, prefix=API_PREFIX)
app.include_router(dashboard.router, prefix=API_PREFIX)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # or restrict to your FE domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# this for debugging 
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors(), "body": exc.body})





@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Customize error code as string of status code
    content = error_response(message=exc.detail, error_code=str(exc.status_code))
    return JSONResponse(status_code=exc.status_code, content=content)

# Optional: catch validation errors (422) for uniform error response
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Optional: detailed error info
    details = []
    for err in exc.errors():
        details.append({
            "field": ".".join(str(loc) for loc in err["loc"] if isinstance(loc, str)),
            "error": err["msg"]
        })

    return JSONResponse(
        status_code=422,
        content=error_response("Validation Error", "422") | {"details": details}
    )

@app.get("/")
def root():
    return {"message": "Welcome to the API backend"}




