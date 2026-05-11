from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates

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
    pool = request.app.state.pool

    repo = SourceRepositoryImpl(pool)

    sources = await repo.list_active()

    return templates.TemplateResponse(
        request,
        "sources.html",
        {
            "sources": sources,
        },
    )
