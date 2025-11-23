import json
import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

from litestar.data_extractors import ResponseExtractorField, RequestExtractorField
from litestar.serialization import decode_json, encode_json
from litestar.utils.module_loader import module_to_os_path
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

BASE_DIR = module_to_os_path()


@dataclass
class PostgresSettings:
    DSN: str = field(default_factory=lambda: os.getenv("POSTGRES_DSN"))

    POOL_MAX_OVERFLOW: int = field(default_factory=lambda: int(os.getenv("DATABASE_MAX_POOL_OVERFLOW", "10")))
    POOL_SIZE: int = field(default_factory=lambda: int(os.getenv("DATABASE_POOL_SIZE", "20")))
    POOL_TIMEOUT: int = field(default_factory=lambda: int(os.getenv("DATABASE_POOL_TIMEOUT", "30")))
    POOL_RECYCLE: int = field(default_factory=lambda: int(os.getenv("DATABASE_POOL_RECYCLE", "300")))

    MIGRATION_CONFIG: str = field(default_factory=lambda: str(Path(BASE_DIR).parent / "app" / "db" / "migrations" / "alembic.ini"))
    MIGRATION_PATH: str = field(default_factory=lambda: str(Path(BASE_DIR).parent / "app" / "db" / "migrations"))
    MIGRATION_DDL_VERSION_TABLE: str = "ddl_version"

    SCHEMA: str = field(default_factory=lambda: os.getenv("POSTGRES_SCHEMA", "public"))

    _engine_instance: AsyncEngine | None = None

    @property
    def engine(self) -> AsyncEngine:
        return self.get_engine()

    def get_engine(self) -> AsyncEngine:
        if self._engine_instance is not None:
            return self._engine_instance
        engine = create_async_engine(
            url=self.DSN,
            future=True,
            json_serializer=encode_json,
            json_deserializer=decode_json,
            max_overflow=self.POOL_MAX_OVERFLOW,
            pool_size=self.POOL_SIZE,
            pool_timeout=self.POOL_TIMEOUT,
            pool_recycle=self.POOL_RECYCLE,
            pool_use_lifo=True,
        )

        @event.listens_for(engine.sync_engine, "connect")
        def _sqla_on_connect(dbapi_connection: Any, _: Any) -> Any:  # pragma: no cover
            def encoder(bin_value: bytes) -> bytes:
                return b"\x01" + encode_json(bin_value)

            def decoder(bin_value: bytes) -> Any:
                return decode_json(bin_value[1:])

            dbapi_connection.await_(
                dbapi_connection.driver_connection.set_type_codec(
                    "jsonb",
                    encoder=encoder,
                    decoder=decoder,
                    schema="pg_catalog",
                    format="binary",
                ),
            )
            dbapi_connection.await_(
                dbapi_connection.driver_connection.set_type_codec(
                    "json",
                    encoder=encoder,
                    decoder=decoder,
                    schema="pg_catalog",
                    format="binary",
                ),
            )

            cursor = dbapi_connection.cursor()
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {self.SCHEMA}")
            cursor.execute(f"SET search_path TO {self.SCHEMA}")
            cursor.execute(f"CREATE EXTENSION IF NOT EXISTS ltree SCHEMA {self.SCHEMA}")
            cursor.close()

        self._engine_instance = engine
        return self._engine_instance


@dataclass
class LogSettings:
    EXCLUDE_PATHS: str = r"\A(?!x)x"
    HTTP_EVENT: str = "HTTP"
    INCLUDE_COMPRESSED_BODY: bool = False
    LEVEL: int = field(default_factory=lambda: int(os.getenv("LOG_LEVEL", "10")))
    REQUEST_FIELDS: list[RequestExtractorField] = field(
        default_factory=lambda: ["method", "path", "path_params", "query", "body"])
    RESPONSE_FIELDS: list[ResponseExtractorField] = field(default_factory=lambda: ["status_code"])
    JSON: bool = field(default_factory=lambda: json.loads(os.getenv("LOG_JSON", "false")))


@dataclass
class AppSettings:
    NAME: str = "no_name"
    VERSION: str = "0"
    DEBUG: bool = field(default_factory=lambda: json.loads(os.getenv("DEBUG", "false")))
    TEST: bool = field(default_factory=lambda: json.loads(os.getenv("TEST", "false")))

    def __post_init__(self):
        pyproject_path = Path(BASE_DIR).parent.parent / "pyproject.toml"
        with open(pyproject_path) as file:
            from app.lib.utils.pyproject import decode, PyProject
            content: PyProject = decode(file.read())
            self.NAME = content.project.name
            self.VERSION = content.project.version


@dataclass
class YooKassaSettings:
    SHOP_ID: str = field(default_factory=lambda: os.getenv("YOOKASSA_SHOP_ID", ""))
    SECRET_KEY: str = field(
        default_factory=lambda: os.getenv("YOOKASSA_SECRET_KEY", "")
    )
    RETURN_URL: str = field(default_factory=lambda: os.getenv("YOOKASSA_RETURN_URL", ""))
    IS_TEST: bool = field(default_factory=lambda: json.loads(os.getenv("YOOKASSA_TEST", "false")))

    def __post_init__(self) -> None:
        if not self.SHOP_ID or not self.SECRET_KEY:
            raise ValueError("YOOKASSA_SHOP_ID и YOOKASSA_SECRET_KEY должны быть установлены")


@dataclass
class EmailSettings:
    SMTP_HOST: str = field(default_factory=lambda: os.getenv("EMAIL_SMTP_HOST", ""))
    SMTP_PORT: int = field(default_factory=lambda: int(os.getenv("EMAIL_SMTP_PORT", "587")))
    SMTP_USER: str = field(default_factory=lambda: os.getenv("EMAIL_SMTP_USER", ""))
    SMTP_PASSWORD: str = field(default_factory=lambda: os.getenv("EMAIL_SMTP_PASSWORD", ""))


@dataclass
class Settings:
    app: AppSettings = field(default_factory=AppSettings)
    postgres: PostgresSettings = field(default_factory=PostgresSettings)
    log: LogSettings = field(default_factory=LogSettings)
    yookassa: YooKassaSettings = field(default_factory=YooKassaSettings)
    email: EmailSettings = field(default_factory=EmailSettings)
    
    @classmethod
    def from_env(cls, env_name=".env") -> "Settings":
        env_path = Path(f"{os.curdir}/{env_name}")
        if env_path.is_file():
            from dotenv import load_dotenv

            load_dotenv(env_path)
        return Settings()


@lru_cache(maxsize=1, typed=True)
def get_settings() -> Settings:
    return Settings.from_env()
