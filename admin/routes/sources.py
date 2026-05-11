from __future__ import annotations

import os

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates

from infrastructure.db.pool import PostgresPool

from sources.repositories.source_repository import (
    SourceRepositoryImpl,
)


router = APIRouter()

templates = Jinja2Templates(
    directory="admin/templates",
)


@router.get(
    "/admin/sources",
    response_class=HTMLResponse,
)
async def list_sources(
    request: Request,
):
    pool = PostgresPool(
        dsn=os.environ["POSTGRES_DSN"],
        logger=None,
    )

    await pool.start()

    repo = SourceRepositoryImpl(pool)

    sources = await repo.list_active()

    return templates.TemplateResponse(
        request,
        "sources.html",
        {
            "sources": sources,
        },
    )
