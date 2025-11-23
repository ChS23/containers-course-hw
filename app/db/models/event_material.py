from __future__ import annotations

from typing import TYPE_CHECKING
from advanced_alchemy.base import BigIntAuditBase
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .event import Event


class EventMaterial(BigIntAuditBase):
    __tablename__ = "event_material"
    __table_args__ = {"comment": "Educational materials for events"}

    title: Mapped[str] = mapped_column(nullable=False)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    is_pro_only: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    event_id: Mapped[int] = mapped_column(ForeignKey("event.id"), nullable=False)
    event: Mapped["Event"] = relationship(
        back_populates="materials",
        lazy="selectin"
    )
    