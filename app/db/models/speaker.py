from __future__ import annotations

from typing import TYPE_CHECKING
from advanced_alchemy.base import BigIntAuditBase
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .event_speaker import EventSpeaker
    from .user import User

class Speaker(BigIntAuditBase):
    __tablename__ = "speaker"
    __table_args__ = {"comment": "Speakers who conduct events"}

    # Может быть null, если спикер регистрируется без создания аккаунта
    user_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), nullable=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Добавляем контактную информацию для спикеров без аккаунта
    contacts: Mapped[str | None] = mapped_column(String(500), nullable=True)

    events: Mapped[list["EventSpeaker"]] = relationship(
        back_populates="speaker",
        lazy="selectin",
        cascade="all, delete",
        passive_deletes=True
    )

    user: Mapped["User"] = relationship(
        back_populates="speaker",
        lazy="selectin"
    )