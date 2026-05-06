from __future__ import annotations

import asyncio
import time
from typing import Sequence

import httpx

from parsers.base.models import RawItem, NormalizedItem
from parsers.base.errors import (
    ParserError,
    RetryableParserError,
    HTTPStatusError,
)
from parsers.base.context import ParserContext, ParserConfig


class BaseParser:
    def __init__(self, normalizer, client: httpx.AsyncClient, config: ParserConfig) -> None:
        self._normalizer = normalizer
        self._client = client
        self._config = config

    async def parse(self, ctx: ParserContext) -> Sequence[NormalizedItem]:
        start = time.time()

        try:
            async with asyncio.timeout(self._config.timeout):
                raw = await self._fetch(ctx)

                raw = raw[: self._config.max_items]

                normalized = await self._normalizer.normalize(raw, ctx.source_id)

                return [item.ensure_utc() for item in normalized]

        except asyncio.TimeoutError:
            raise RetryableParserError("timeout")

        finally:
            duration = time.time() - start
            # observability hook
            # log parse duration externally

    async def _get(self, ctx: ParserContext) -> httpx.Response:
        headers = {}

        if ctx.etag:
            headers["If-None-Match"] = ctx.etag
        if ctx.last_modified:
            headers["If-Modified-Since"] = ctx.last_modified

        response = await self._client.get(ctx.url, headers=headers)

        if response.status_code == 304:
            return response

        if 500 <= response.status_code < 600:
            raise HTTPStatusError(response.status_code)

        if response.status_code >= 400:
            raise ParserError(f"http_{response.status_code}")

        return response

    async def _fetch(self, ctx: ParserContext) -> Sequence[RawItem]:
        raise NotImplementedError
