from __future__ import annotations

import os
import asyncio

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from database.models.base import Base

# Import ALL models so metadata is populated
from database.models.chats import Chat
from database.models.sources import Source
from database.models.publications import Publication
from database.models.subscriptions import Subscription
from database.models.topics import Topic
from database.models.outbox import Outbox

from database.models.source_health import SourceHealthRecord

config = context.config

# --- FIX: enforce asyncpg dialect ---
database_url = os.getenv("POSTGRES_DSN", "").strip()

if database_url.startswith("postgresql://"):
    database_url = database_url.replace(
        "postgresql://",
        "postgresql+asyncpg://",
        1,
    )

if database_url.startswith("postgresql+psycopg2://"):
    database_url = database_url.replace(
        "postgresql+psycopg2://",
        "postgresql+asyncpg://",
        1,
    )

config.set_main_option("sqlalchemy.url", database_url)

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async def do_run():
        async with connectable.connect() as connection:
            await connection.run_sync(run_sync_migrations)

    asyncio.run(do_run())


def run_sync_migrations(connection: Connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
