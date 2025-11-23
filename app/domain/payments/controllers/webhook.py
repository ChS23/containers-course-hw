from litestar import Controller, post

from app.domain.events.services import EventService
from app.domain.payments.services import PaymentService
from app.domain.registrations.services import EventTicketService
from app.lib.deps import create_service_provider
from app.services.yookassa import YooKassaService


class WebhookController(Controller):
    path = "/webhook"

    tags = ["PaymentsWebhook"]
    dependencies = {
        "event_ticket_service": create_service_provider(EventTicketService),
        "event_service": create_service_provider(EventService),
        "payment_service": create_service_provider(PaymentService)
    }

    @post(operation_id="new_payment")
    async def new_payment(
            self,
            event_ticket_service: EventTicketService,
            event_service: EventService,
            payment_service: PaymentService,
            data: dict
    ) -> None:
        if data["event"] == "payment.succeeded":
            return await YooKassaService.unregister_payment_with_site(
                event_ticket_service,
                event_service,
                payment_service,
                data
            )

