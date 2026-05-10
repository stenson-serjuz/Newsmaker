from __future__ import annotations

import asyncio
import time
from uuid import UUID, uuid4

import httpx

from redis.asyncio import Redis

from parsers.base.context import ParserContext, ParserConfig
from parsers.normalizers.normalizer import Normalizer
from parsers.registry.registry import ParserRegistry

from parsers.rss.advanced_rss_parser import AdvancedRSSParser

from runtime.scheduler import Scheduler
from runtime.event_dispatcher import EventDispatcher
from runtime.runtime_manager import RuntimeManager

from infrastructure.queue.producer import StreamProducer

from contracts.events.envelope import EventEnvelope
from contracts.events.retry import RetryMetadata
from contracts.events.delivery import DeliveryMetadata


RSS_URL = "https://russian.korea.net/koreanet/rss/news/2"


# -----------------------------------------------------------------------------
# SIMPLE LOGGER
# -----------------------------------------------------------------------------

class SimpleLogger:
    def bind(self, **kwargs):
        return self

    def info(self, *args, **kwargs):
        print("[INFO]", args, kwargs)

    def warning(self, *args, **kwargs):
        print("[WARN]", args, kwargs)

    def error(self, *args, **kwargs):
        print("[ERROR]", args, kwargs)


logger = SimpleLogger()


# -----------------------------------------------------------------------------
# STATIC SOURCE
# -----------------------------------------------------------------------------

class StaticSource:
    def __init__(self) -> None:
        self.id = uuid4()
        self.is_active = True
        self.is_degraded = False
        self.parser_key = "advanced_rss"
        self.url = RSS_URL


# -----------------------------------------------------------------------------
# SOURCE PROVIDER
# -----------------------------------------------------------------------------

class StaticSourceProvider:
    def __init__(self, source: StaticSource) -> None:
        self._source = source

    async def list_active(self):
        return [self._source]


# -----------------------------------------------------------------------------
# SOURCE SERVICE
# -----------------------------------------------------------------------------

class StaticSourceService:
    def __init__(
        self,
        source: StaticSource,
        registry: ParserRegistry,
    ) -> None:
        self._source = source
        self._registry = registry

    async def bind_parser(self, source_id: UUID):
        return self._registry.get(self._source.parser_key)

    async def get_context(self, source_id: UUID) -> ParserContext:
        return ParserContext(
            source_id=source_id,
            url=self._source.url,
        )

    async def mark_success(self, source_id: UUID) -> None:
        print(f"[SOURCE] success: {source_id}")

    async def mark_failure(self, source_id: UUID) -> None:
        print(f"[SOURCE] failure: {source_id}")


# -----------------------------------------------------------------------------
# NOOP DEDUP
# -----------------------------------------------------------------------------

class NoOpDedup:
    async def is_duplicate(self, item) -> bool:
        return False


# -----------------------------------------------------------------------------
# EVENT PRODUCER WRAPPER
# -----------------------------------------------------------------------------

class EventProducer:
    def __init__(self, producer: StreamProducer) -> None:
        self._producer = producer

    async def publish(self, stream: str, event: dict) -> str:
        envelope = EventEnvelope(
            schema_version=1,
            event_id=str(uuid4()),
            trace_id=None,
            payload=event,
            metadata={
                "source": "rss_runtime",
            },
            retry=RetryMetadata(),
            delivery=DeliveryMetadata(
                shard_id=0,
                created_at=int(time.time()),
            ),
        )

        return await self._producer.publish(stream, envelope)


# -----------------------------------------------------------------------------
# CUSTOM PARSER RUNNER
# -----------------------------------------------------------------------------

class RSSParserRunner:
    def __init__(
        self,
        source_service: StaticSourceService,
        dispatcher,
        logger,
    ) -> None:
        self._sources = source_service
        self._dispatcher = dispatcher
        self._logger = logger.bind(component="parser_runner")

    async def run(self, source_id: UUID) -> None:
        start = time.monotonic()

        parser = await self._sources.bind_parser(source_id)

        ctx = await self._sources.get_context(source_id)

        try:
            items = await parser.parse(ctx)

            print(f"\n[RSS] parsed items: {len(items)}\n")

            await self._dispatcher.dispatch(source_id, items)

            await self._sources.mark_success(source_id)

        except Exception as e:
            await self._sources.mark_failure(source_id)

            self._logger.error(
                "parser_failed",
                source_id=str(source_id),
                error=str(e),
            )

        finally:
            duration = time.monotonic() - start

            self._logger.info(
                "parser_completed",
                source_id=str(source_id),
                duration=duration,
            )


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

async def main() -> None:
    print("Starting RSS runtime...\n")

    redis = Redis.from_url(
        "redis://localhost:6379",
        encoding="utf-8",
        decode_responses=True,
    )

    registry = ParserRegistry()

    client = httpx.AsyncClient(
        timeout=20.0,
        follow_redirects=True,
    )

    registry.register(
        "advanced_rss",
        lambda: AdvancedRSSParser(
            normalizer=Normalizer(),
            client=client,
            config=ParserConfig(
                timeout=20.0,
                max_items=10,
            ),
        ),
    )

    source = StaticSource()

    source_service = StaticSourceService(
        source=source,
        registry=registry,
    )

    dispatcher = EventDispatcher(
        producer=EventProducer(
            StreamProducer(redis),
        ),
        dedup=NoOpDedup(),
        logger=logger,
    )

    runner = RSSParserRunner(
        source_service=source_service,
        dispatcher=dispatcher,
        logger=logger,
    )

    scheduler = Scheduler(
        provider=StaticSourceProvider(source),
        runner=runner,
        interval=60.0,
        concurrency=1,
    )

    runtime = RuntimeManager(
        scheduler=scheduler,
        logger=logger,
    )

    await runtime.start()

    print("RSS runtime started.\n")

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
