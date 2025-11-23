from __future__ import annotations

from typing import TYPE_CHECKING

import datetime
from advanced_alchemy.base import BigIntAuditBase
from advanced_alchemy.mixins import SlugKey
from advanced_alchemy.types import DateTimeUTC
from sqlalchemy import String, Numeric, CheckConstraint, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .event_speaker import EventSpeaker
    from .event_material import EventMaterial
    from .event_ticket import EventTicket


class Event(BigIntAuditBase, SlugKey):
    __tablename__ = "event"
    __table_args__ = (
        CheckConstraint("price >= 0", name="check_price_positive"),
        CheckConstraint("pro_price >= 0", name="check_pro_price_positive"),
        CheckConstraint("pro_price <= price", name="check_pro_price_less_than_price"),
        CheckConstraint("max_participants > 0", name="check_max_participants_positive"),
        {"comment": "Educational events"}
    )

    title: Mapped[str] = mapped_column(nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(length=500), nullable=True, default=None)
    cover_url: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)

    price: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    pro_price: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)

    event_date: Mapped[datetime.datetime] = mapped_column(
        DateTimeUTC(timezone=True),
        nullable=False,
        index=True
    )
    location: Mapped[str] = mapped_column(String(255), nullable=False)

    max_participants: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chat_link: Mapped[str | None] = mapped_column(String(255), nullable=True)

    registrations: Mapped[list["EventTicket"]] = relationship(
        back_populates="event",
        lazy="selectin",
        cascade="all, delete",
        passive_deletes=True
    )
    materials: Mapped[list["EventMaterial"]] = relationship(
        back_populates="event",
        lazy="selectin",
        cascade="all, delete",
        passive_deletes=True
    )
    speakers: Mapped[list["EventSpeaker"]] = relationship(
        back_populates="event",
        lazy="selectin",
        cascade="all, delete",
        passive_deletes=True
    )
