from __future__ import annotations

from typing import Protocol, AsyncIterator

from contracts.events.envelope import EventEnvelope


class ProducerProtocol(Protocol):
    async def publish(self, stream: str, event: EventEnvelope) -> str: ...


class ConsumerProtocol(Protocol):
    async def start(self) -> None: ...
    async def stop(self) -> None: ...

    async def consume(self) -> AsyncIterator[tuple[str, EventEnvelope]]: ...

    async def ack(self, message_id: str) -> None: ...
