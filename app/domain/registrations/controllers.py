from __future__ import annotations

from typing import Annotated, TYPE_CHECKING

from litestar import Controller, post
from litestar.params import Body
from litestar.openapi.spec import Example
from litestar.di import Provide

from app.lib.deps import create_service_provider
from app.domain.registrations.services import EventTicketService
from app.db.models import EventTicket
from app.domain.registrations.schemas \
    import UnregisteredUserRegistrationSchema, \
        RegistrationResponseSchema
from app.db.models.user import User
from app.db.models.event import Event
from app.domain.accounts.services import UserService
from app.domain.events.services import EventService
from app.services.yookassa import YooKassaClient, Payment, CreatePayment, Amount, Confirmation
from app.db.models.event_ticket import EventTicketStatus

if TYPE_CHECKING:
    from advanced_alchemy.service.pagination import OffsetPagination
    from litestar.params import Dependency, Parameter


class RegistrationController(Controller):
    tags = ["Registrations"]
    dependencies = {
        "event_ticket_service": create_service_provider(
            EventTicketService,
            load=[EventTicket.event, EventTicket.user, EventTicket.payment]
        ),
        "user_service": create_service_provider(
            UserService,
            load=[User.tickets, User.speaker, User.pro_subscriptions]
        ),
        "event_service": create_service_provider(
            EventService,
            load=[Event.registrations]
        )
    }

    @post("/register/unregistered")
    async def register_unregistered(
        self,
        event_ticket_service: EventTicketService,
        user_service: UserService,
        event_service: EventService,
        data: Annotated[
            UnregisteredUserRegistrationSchema, 
            Body(
                examples=[
                    Example(
                        description="Регистрация нового участника на мероприятие",
                        value=UnregisteredUserRegistrationSchema(
                            email="user@example.com",
                            first_name="Иван",
                            last_name="Иванов",
                            event_id=5,
                            contact_info="Мой tg: @example",
                            source="test@site.com"
                        )
                    )
                ]
            )
        ]
    ) -> RegistrationResponseSchema:
        # 1. Создаем пользователя
        user = await user_service.create({
            "email": data.email,
            "first_name": data.first_name,
            "last_name": data.last_name,
            "contact_info": data.contact_info
        })
        
        # Получаем событие по id
        event = await event_service.get_one(
            id=data.event_id
        )
        
        # 2. Создаем билет
        ticket = await event_ticket_service.create({
            "event_id": event.id,
            "user_id": user.id,
            "status": EventTicketStatus.WAITING_PAYMENT,
            "amount_paid": event.price
        })
        
        # 3. Создаем платеж и получаем ссылку на оплату
        payment: Payment = await YooKassaClient.create_payment(
            payment=CreatePayment(
                amount=Amount(
                    value=float(event.price),
                    currency="RUB"
                ),
                confirmation=Confirmation(
                    type="redirect",
                    return_url="https://example.com"
                ),
                save_payment_method=False,
                capture=True,
                description=f"Оплата участия в мероприятии {event.title}",
                metadata={
                    "ticket_id": str(ticket.id),
                    "event_id": str(event.id),
                    "user_id": str(user.id),
                    "source": data.source
                }
            )
        )
        
        return RegistrationResponseSchema(payment_url=payment.confirmation["confirmation_url"])
        