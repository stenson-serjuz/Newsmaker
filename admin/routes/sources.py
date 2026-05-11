from __future__ import annotations

import uuid

from fastapi import APIRouter
from fastapi import Form
from fastapi import Request

from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse

from fastapi.templating import Jinja2Templates

from database.models.enums import SourceTypeEnum

from sources.models.source import SourceModel

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


@router.get(
    "/admin/sources/new",
    response_class=HTMLResponse,
)
async def create_source_page(
    request: Request,
):
    return templates.TemplateResponse(
        request,
        "source_create.html",
        {},
    )


@router.post(
    "/admin/sources/new",
)
async def create_source(
    request: Request,
    name: str = Form(...),
    type: str = Form(...),
    url: str = Form(...),
    parser_key: str = Form(...),
):
    pool = request.app.state.pool

    repo = SourceRepositoryImpl(pool)

    source = SourceModel(
        id=uuid.uuid4(),
        name=name,
        type=SourceTypeEnum(type),
        url=url,
        parser_key=parser_key,
        is_active=True,
    )

    await repo.add(source)

    return RedirectResponse(
        url="/admin/sources",
        status_code=303,
    )
