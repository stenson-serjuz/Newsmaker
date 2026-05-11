from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from admin.routes.sources import router as sources_router


app = FastAPI(
    title="Newsmaker Admin",
)


app.mount(
    "/static",
    StaticFiles(directory="admin/static"),
    name="static",
)

templates = Jinja2Templates(
    directory="admin/templates",
)

app.include_router(
    sources_router,
)
