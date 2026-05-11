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


@router.get(
    "/admin/debug/publications",
    response_class=HTMLResponse,
)
async def debug_publications(
    request: Request,
):
    pool = request.app.state.pool

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT
                id,
                source_id,
                external_id,
                delivery_state,
                retry_count
            FROM publications
            ORDER BY created_at DESC
            LIMIT 50
            """
        )

    html = """
    <html>
    <body>
        <h1>Publications</h1>
        <table border="1" cellpadding="8">
            <tr>
                <th>ID</th>
                <th>Source</th>
                <th>External ID</th>
                <th>Status</th>
            </tr>
    """

    for row in rows:
        html += f"""
        <tr>
            <td>{row["id"]}</td>
            <td>{row["source_id"]}</td>
            <td>{row["external_id"]}</td>
            <td>{row["delivery_state"]}</td>
        </tr>
        """

    html += """
        </table>
    </body>
    </html>
    """

    return HTMLResponse(content=html)
