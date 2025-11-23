from __future__ import annotations

from typing import TYPE_CHECKING

from advanced_alchemy.repository import (
    SQLAlchemyAsyncRepository
)
from advanced_alchemy.service import (
    SQLAlchemyAsyncRepositoryService,
)
    
from app.db import models

if TYPE_CHECKING:
    from advanced_alchemy.service import ModelDictT

__all__ = ("EventTicketService",)


class EventTicketService(SQLAlchemyAsyncRepositoryService[models.EventTicket]):
    class EventTicketRepository(SQLAlchemyAsyncRepository[models.EventTicket]):
        model_type = models.EventTicket
    repository_type = EventTicketRepository
