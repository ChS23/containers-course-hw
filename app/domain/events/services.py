from __future__ import annotations

from typing import TYPE_CHECKING

from advanced_alchemy.repository import (
    SQLAlchemyAsyncSlugRepository
)
from advanced_alchemy.service import (
    SQLAlchemyAsyncRepositoryService,
    is_dict_with_field,
    is_dict_without_field,
    schema_dump,
)
from slugify import slugify

from app.db import models

if TYPE_CHECKING:
    from advanced_alchemy.service import ModelDictT

__all__ = ("EventService",)


class EventService(SQLAlchemyAsyncRepositoryService[models.Event]):
    class EventRepository(SQLAlchemyAsyncSlugRepository[models.Event]):
        model_type = models.Event
    repository_type = EventRepository

    match_fields = ["title"]
    
    async def to_model_on_create(self, data: ModelDictT[models.Event]) -> ModelDictT[models.Event]:
        data = schema_dump(data)
        return await self._populate_slug(data)
    
    async def to_model_on_update(self, data: ModelDictT[models.Event]) -> ModelDictT[models.Event]:
        data = schema_dump(data)
        return await self._populate_slug(data)
    
    async def to_model_on_upsert(self, data: ModelDictT[models.Event]) -> ModelDictT[models.Event]:
        data = schema_dump(data)
        return await self._populate_slug(data)

    async def _populate_slug(self, data: ModelDictT[models.Event]) -> ModelDictT[models.Event]:
        if is_dict_without_field(data, "slug") and is_dict_with_field(data, "title"):
            data["slug"] = slugify(text=data["title"])
        return data
