from __future__ import annotations

from typing import TYPE_CHECKING

from advanced_alchemy.repository import (
    SQLAlchemyAsyncRepository
)
from advanced_alchemy.service import (
    SQLAlchemyAsyncRepositoryService
)

from app.db import models

if TYPE_CHECKING:
    from advanced_alchemy.service import ModelDictT

__all__ = ("EventMaterialService",)


class EventMaterialService(SQLAlchemyAsyncRepositoryService[models.EventMaterial]):
    class EventMaterialRepository(SQLAlchemyAsyncRepository[models.EventMaterial]):
        model_type = models.EventMaterial
    repository_type = EventMaterialRepository
    