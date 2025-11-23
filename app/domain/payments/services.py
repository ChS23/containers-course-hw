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

__all__ = ("PaymentService",)


class PaymentService(SQLAlchemyAsyncRepositoryService[models.Payment]):
    class PaymentRepository(SQLAlchemyAsyncRepository[models.Payment]):
        model_type = models.Payment
    repository_type = PaymentRepository
    