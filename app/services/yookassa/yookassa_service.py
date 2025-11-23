from __future__ import annotations

from typing import TYPE_CHECKING
from litestar.response import Response

from app.domain.events.services import EventService
from app.domain.payments.services import PaymentService
from app.domain.registrations.services import EventTicketService
from app.db.models.payment import PaymentStatus, PaymentSource, PaymentType
from app.db.models.event_ticket import EventTicketStatus
from app.services.email.email_service import EmailService
from app.db.models.payment import Payment
if TYPE_CHECKING:
    from app.domain.events.services import EventService
    from app.domain.registrations.services import EventTicketService
    from app.domain.payments.services import PaymentService


class YooKassaService:
    @classmethod
    async def unregister_payment_with_site(
            cls,
            event_ticket_service: EventTicketService,
            event_service: EventService,
            payment_service: PaymentService,
            data: dict
    ) -> Response:
        metadata = data["object"]["metadata"]
        ticket_id = int(metadata["ticket_id"])
        print(data)
        
        # 1. Создать платеж в базе
        payment_data = {
            "yookassa_id": data["object"]["id"],
            "amount": data["object"]["amount"]["value"],
            "payment_status": PaymentStatus.SUCCEEDED,
            "payment_source": PaymentSource.WEBSITE,
            "payment_type": PaymentType.EVENT_TICKET,
            "payment_metadata": {
                "event_id": int(metadata["event_id"]),
                "user_id": int(metadata["user_id"]),
                "ticket_id": ticket_id,
                "source": metadata["source"]
            },
            "ticket_id": ticket_id
        }
        _ = await payment_service.create(data=payment_data)

        # 2. Обновить статус билета
        ticket = await event_ticket_service.get_one(id=ticket_id)
        event_ticket_data = await event_ticket_service.get_one(id=ticket_id)
        event_ticket_data.amount_paid = data["object"]["amount"]["value"]
        event_ticket_data.status = EventTicketStatus.PAID
        await event_ticket_service.update(
            item_id=ticket_id,
            data=event_ticket_data.to_dict()
        )

        # 3. Отправка сообщения на почту с билетом на мероприятие
        await EmailService.send_ticket_to_email(ticket)
        
        return Response(
            content="OK",
            status_code=200
        )
    
    @classmethod
    async def register_payment_with_site(cls, payment_id: str) -> None:
        pass
