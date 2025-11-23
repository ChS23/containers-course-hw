from advanced_alchemy.base import orm_registry
from advanced_alchemy.extensions.litestar import (
    AlembicAsyncConfig,
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
)

from app.config.settings import get_settings

settings = get_settings()


orm_registry.metadata.schema = settings.postgres.SCHEMA

alchemy = SQLAlchemyAsyncConfig(
    engine_instance=settings.postgres.get_engine(),
    before_send_handler="autocommit",
    session_dependency_key="db_session",
    session_config=AsyncSessionConfig(
        expire_on_commit=False
    ),
    alembic_config=AlembicAsyncConfig(
        version_table_name=settings.postgres.MIGRATION_DDL_VERSION_TABLE,
        script_config=settings.postgres.MIGRATION_CONFIG,
        script_location=settings.postgres.MIGRATION_PATH,
        version_table_schema=settings.postgres.SCHEMA,
    ),
    metadata=orm_registry.metadata,
)
