import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from pathlib import Path

is_running_in_docker = os.path.exists("/.dockerenv") or os.environ.get("DOCKER") is not None

num_of_parents = [4, 1][is_running_in_docker]

PROJECT_ROOT = Path(__file__).resolve().parents[num_of_parents]
sys.path.append(str(PROJECT_ROOT))

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from conf.settings import settings
from models import Base
import models  # noqa

target_metadata = Base.metadata

URL = "sqlalchemy.url"


def assign_url() -> None:
    options = [settings.pg.dsn_local, settings.pg.dsn][is_running_in_docker]

    if URL not in config.get_section(config.config_ini_section):
        config.set_main_option(URL, f"{options}?async_fallback=True")


assign_url()


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"}
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
