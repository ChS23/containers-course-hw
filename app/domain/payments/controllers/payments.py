from litestar import Controller, post

from app.lib.deps import create_service_dependencies
from app.domain.payments.services import PaymentService
from app.db.models import Payment

class PaymentController(Controller):
    tags = ["Payments"]
    dependencies = create_service_dependencies(
        PaymentService,
        key="payment_service"
    )

    @post("/")
    async def create_payment(
        self,
        payment_service: PaymentService,
        payment: Payment
    ) -> Payment:
        ...