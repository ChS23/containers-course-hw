from __future__ import annotations

from typing import TYPE_CHECKING
import datetime
from advanced_alchemy.base import BigIntAuditBase
from sqlalchemy import ForeignKey, CheckConstraint
from advanced_alchemy.types import DateTimeUTC
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .user import User
    from .payment import Payment


class ProSubscription(BigIntAuditBase):
    __tablename__ = "pro_subscription"
    __table_args__ = (
        CheckConstraint(
            "starts_at < expires_at",
            name="check_subscription_dates"
        ),
        {"comment": "Pro subscription records"}
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    starts_at: Mapped[datetime.datetime] = mapped_column(
        DateTimeUTC(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    expires_at: Mapped[datetime.datetime] = mapped_column(
        DateTimeUTC(timezone=True),
        nullable=False
    )

    user: Mapped["User"] = relationship(
        back_populates="pro_subscriptions",
        lazy="selectin"
    )
    payment: Mapped["Payment | None"] = relationship(
        back_populates="subscription",
        lazy="selectin",
        uselist=False
    ) 
    