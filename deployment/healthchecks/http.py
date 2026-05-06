from __future__ import annotations

from aiohttp import web


async def health(request):
    return web.json_response({"status": "ok"})


async def readiness(request):
    return web.json_response({"ready": True})


def create_app():
    app = web.Application()
    app.router.add_get("/health", health)
    app.router.add_get("/ready", readiness)
    return app
