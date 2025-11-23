from __future__ import annotations

from typing import TYPE_CHECKING
from advanced_alchemy.base import BigIntAuditBase
from sqlalchemy import ForeignKey, Boolean, Numeric, CheckConstraint, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import StrEnum

if TYPE_CHECKING:
    from .event import Event
    from .user import User
    from .payment import Payment


class EventTicketStatus(StrEnum):
    WAITING_PAYMENT = "waiting_payment"
    PAID = "paid"
    REFUNDED = "refunded"


class EventTicket(BigIntAuditBase):
    __tablename__ = "event_ticket"
    __table_args__ = (
        CheckConstraint("amount_paid >= 0", name="check_amount_paid_positive"),
        UniqueConstraint("event_id", "user_id", name="uq_event_user"),
        {"comment": "Event registration tickets"}
    )

    event_id: Mapped[int] = mapped_column(ForeignKey("event.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    amount_paid: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    status: Mapped[EventTicketStatus] = mapped_column(
        Enum(EventTicketStatus, native_enum=False, length=30),
        nullable=False,
        default=EventTicketStatus.WAITING_PAYMENT
    )

    event: Mapped["Event"] = relationship(
        back_populates="registrations",
        lazy="selectin"
    )
    user: Mapped["User"] = relationship(
        back_populates="tickets",
        lazy="selectin"
    )
    payment: Mapped["Payment | None"] = relationship(
        back_populates="ticket",
        uselist=False
    )
