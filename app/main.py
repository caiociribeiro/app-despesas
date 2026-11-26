from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import APP_NAME
from app.routers.health import router as health_router
from app.routers.categories import router as categories_router
from app.routers.payment_methods import router as payment_methods_router
from app.routers.expenses import router as expenses_router
from app.routers.establishments import router as establishments_router
from app.routers.dashboard import router as dashboard_router
from app.routers.tags import router as tags_router

app = FastAPI(title=APP_NAME, version="0.2.0")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(health_router)
app.include_router(categories_router)
app.include_router(payment_methods_router)
app.include_router(expenses_router)
app.include_router(establishments_router)
app.include_router(dashboard_router)
app.include_router(tags_router)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"app_name": APP_NAME})


@app.get("/categories", response_class=HTMLResponse)
def categories_page(request: Request):
    return templates.TemplateResponse(request=request, name="categories.html", context={"app_name": APP_NAME})
