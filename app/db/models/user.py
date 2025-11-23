from __future__ import annotations

from typing import TYPE_CHECKING

import datetime
from advanced_alchemy.base import BigIntAuditBase
from advanced_alchemy.types import DateTimeUTC
from sqlalchemy import UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

if TYPE_CHECKING:
    from .event_ticket import EventTicket
    from .pro_subscription import ProSubscription
    from .speaker import Speaker


class User(BigIntAuditBase):
    __tablename__ = "user"
    __table_args__ = (
        UniqueConstraint("email", name="uq_user_email"),
        UniqueConstraint("telegram_id", name="uq_user_telegram"),
        CheckConstraint(
            "(is_pro = false AND pro_expired_at IS NULL) OR "
            "(is_pro = true AND pro_expired_at > CURRENT_TIMESTAMP)",
            name="check_pro_status"
        ),
        {"comment": "Users of the application"}
    )
    __pii_columns__ = {"first_name", "last_name", "email", "telegram_id", "contact_info"}

    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)

    email: Mapped[str | None] = mapped_column(nullable=True)
    telegram_id: Mapped[str | None] = mapped_column(nullable=True)
    contact_info: Mapped[str | None] = mapped_column(nullable=True)
    is_pro: Mapped[bool] = mapped_column(nullable=False, default=False)
    pro_expired_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTimeUTC(timezone=True),
        nullable=True
    )

    pro_subscriptions: Mapped[list["ProSubscription"]] = relationship(
        back_populates="user",
        lazy="selectin",
        cascade="all, delete"
    )
    speaker: Mapped["Speaker | None"] = relationship(
        back_populates="user",
        lazy="selectin",
        uselist=False
    )
    tickets: Mapped[list["EventTicket"]] = relationship(
        back_populates="user",
        lazy="selectin",
        cascade="all, delete"
    )

    @hybrid_property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
