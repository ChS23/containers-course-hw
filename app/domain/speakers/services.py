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

__all__ = ("SpeakerService",)


class SpeakerService(SQLAlchemyAsyncRepositoryService[models.Speaker]):
    class SpeakerRepository(SQLAlchemyAsyncRepository[models.Speaker]):
        model_type = models.Speaker
    repository_type = SpeakerRepository
    