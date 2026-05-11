from __future__ import annotations

import os

from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from infrastructure.db.pool import PostgresPool

from admin.routes.sources import router as sources_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = PostgresPool(
        dsn=os.environ["POSTGRES_DSN"],
        logger=None,
    )

    await pool.start()

    app.state.pool = pool

    yield

    await pool.close()


app = FastAPI(
    title="Newsmaker Admin",
    lifespan=lifespan,
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
