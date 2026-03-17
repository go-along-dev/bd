<<<<<<< HEAD
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from app.db.postgres import Base
from app.models.user import User
from app.models.driver import Driver
from app.models.driver_document import DriverDocument
from app.models.ride import Ride
from app.models.booking import Booking
from app.models.wallet import Wallet
from app.models.wallet_transaction import WalletTransaction
from app.models.platform_config import PlatformConfig

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
=======
# =============================================================================
# alembic/env.py — Alembic Migration Environment
# =============================================================================
# See: system-design/11-db-schema-ddl.md §16 "Migration Checklist"
# See: system-design/00-architecture.md §8 note 5 — "Alembic manages schema, not Supabase Dashboard"
#
# Alembic connects to the same Supabase PostgreSQL as the app.
# Auto-generates migrations by comparing models to actual DB schema.
#
# TODO: Import Base.metadata from app.db.base
#       (Ensure all models are imported in app/models/__init__.py so Alembic discovers them)
#
# TODO: Configure target_metadata = Base.metadata
#
# TODO: def run_migrations_offline():
#       """Generate SQL without connecting to DB. For review before applying."""
#
# TODO: async def run_migrations_online():
#       """Connect to DB and apply migrations."""
#       - Use config.SUPABASE_DB_URL (from alembic.ini or env var)
#       - Must use async engine: create_async_engine + run_sync
#
# TODO: First migration should:
#       1. Create all 8 tables (copy DDL from 11-db-schema-ddl.md)
#       2. Create pgcrypto extension
#       3. Create auto-update trigger for updated_at columns
#       4. Seed platform_config with initial values
#
# Commands:
#   alembic revision --autogenerate -m "initial schema"
#   alembic upgrade head
#
# Connects with:
#   → app/db/base.py (Base.metadata)
#   → app/models/*.py (all models must be imported for autogenerate)
#   → app/config.py (SUPABASE_DB_URL)
#   → alembic.ini (points to this env.py)
#
# work by adolf.
>>>>>>> 0e6b5450dd33373090fa841d0d339a07852dc2d5
