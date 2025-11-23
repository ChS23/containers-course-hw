from __future__ import annotations

from typing import TYPE_CHECKING
from enum import StrEnum
from advanced_alchemy.base import BigIntAuditBase
from sqlalchemy import String, Numeric, Enum, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

if TYPE_CHECKING:
    from .event_ticket import EventTicket
    from .pro_subscription import ProSubscription


class PaymentStatus(StrEnum):
    PENDING = "pending"
    WAITING_FOR_CAPTURE = "waiting_for_capture"
    SUCCEEDED = "succeeded"
    CANCELED = "canceled"
    FAILED = "failed"

    @classmethod
    def values(cls) -> list[str]:
        return [status.value for status in cls]


class PaymentSource(StrEnum):
    WEBSITE = "website"
    TELEGRAM = "telegram" 
    ADMIN = "admin"

    @classmethod
    def values(cls) -> list[str]:
        return [source.value for source in cls]


class PaymentType(StrEnum):
    EVENT_TICKET = "event_ticket"
    PRO_SUBSCRIPTION = "pro_subscription"

    @classmethod
    def values(cls) -> list[str]:
        return [type.value for type in cls]


class Payment(BigIntAuditBase):
    __tablename__ = "payment"
    __table_args__ = (
        CheckConstraint(
            "(ticket_id IS NOT NULL AND subscription_id IS NULL) OR (ticket_id IS NULL AND subscription_id IS NOT NULL)",
            name="check_payment_target"
        ),
        CheckConstraint("amount >= 0", name="check_amount_positive"),
        {"comment": "Payment records for tickets and subscriptions"}
    )

    ticket_id: Mapped[int | None] = mapped_column(ForeignKey("event_ticket.id"), nullable=True)
    subscription_id: Mapped[int | None] = mapped_column(ForeignKey("pro_subscription.id"), nullable=True)
    yookassa_id: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, native_enum=False, length=30), 
        nullable=False, 
        default=PaymentStatus.PENDING
    )
    payment_source: Mapped[str] = mapped_column(
        Enum(PaymentSource, native_enum=False, length=30),
        nullable=False,
        default=PaymentSource.ADMIN,
    )
    payment_type: Mapped[str] = mapped_column(
        Enum(PaymentType, native_enum=False, length=30),
        nullable=False,
        default=PaymentType.EVENT_TICKET,
    )
    payment_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default={})

    ticket: Mapped["EventTicket | None"] = relationship(
        back_populates="payment",
        lazy="selectin",
        uselist=False
    )
    subscription: Mapped["ProSubscription | None"] = relationship(
        back_populates="payment",
        lazy="selectin",
        uselist=False
    )

    @hybrid_property
    def is_ticket_payment(self) -> bool:
        return self.payment_type == PaymentType.EVENT_TICKET

    @hybrid_property
    def is_subscription_payment(self) -> bool:
        return self.payment_type == PaymentType.PRO_SUBSCRIPTION
    