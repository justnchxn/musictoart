from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from .auth import router as auth_router
from .spotify import get_tokens
from .generate import router as gen_router
from .config import STABILITY_API_KEY, STABILITY_MODEL

app = FastAPI()

# Routers
app.include_router(auth_router)
app.include_router(gen_router)

# Serve generated images from /static/generated
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    authed = bool(get_tokens(request))
    return templates.TemplateResponse("index.html", {"request": request, "authed": authed})

@app.get("/health")
def health():
    return {
        "stability_key_present": bool(STABILITY_API_KEY),
        "model": STABILITY_MODEL,
    }
