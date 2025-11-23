from __future__ import annotations

from typing import TYPE_CHECKING
from advanced_alchemy.base import BigIntAuditBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .event import Event
    from .speaker import Speaker


class EventSpeaker(BigIntAuditBase):
    __tablename__ = "event_speaker"
    __table_args__ = {"comment": "Association table for events and speakers"}

    event_id: Mapped[int] = mapped_column(ForeignKey("event.id", ondelete="CASCADE"), nullable=False)
    speaker_id: Mapped[int] = mapped_column(ForeignKey("speaker.id", ondelete="CASCADE"), nullable=False)

    event: Mapped["Event"] = relationship(
        back_populates="speakers",
        lazy="selectin"
    )
    speaker: Mapped["Speaker"] = relationship(
        back_populates="events",
        lazy="selectin"
    )
    