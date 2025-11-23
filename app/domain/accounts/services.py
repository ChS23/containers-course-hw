from __future__ import annotations

from typing import TYPE_CHECKING

from advanced_alchemy.repository import (
    SQLAlchemyAsyncRepository
)
from advanced_alchemy.service import (
    SQLAlchemyAsyncRepositoryService
)

from app.db import models

__all__ = ("UserService",)


class UserService(SQLAlchemyAsyncRepositoryService[models.User]):
    class UserRepository(SQLAlchemyAsyncRepository[models.User]):
        model_type = models.User
    repository_type = UserRepository
