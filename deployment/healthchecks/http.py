from __future__ import annotations

from aiohttp import web

from infrastructure.db.health import PostgresHealthCheck
from infrastructure.redis.health import RedisHealthCheck


class HealthApp:
    def __init__(
        self,
        pg: PostgresHealthCheck,
        redis: RedisHealthCheck,
    ) -> None:
        self._pg = pg
        self._redis = redis

    async def health(self, request: web.Request) -> web.Response:
        return web.json_response({"status": "ok"})

    async def readiness(self, request: web.Request) -> web.Response:
        pg_ok, redis_ok = await asyncio.gather(
            self._pg.check(),
            self._redis.check(),
        )

        status = 200 if (pg_ok and redis_ok) else 503

        return web.json_response(
            {
                "postgres": pg_ok,
                "redis": redis_ok,
            },
            status=status,
        )


def create_app(pg, redis):
    h = HealthApp(pg, redis)
    app = web.Application()
    app.router.add_get("/health", h.health)
    app.router.add_get("/ready", h.readiness)
    return app
