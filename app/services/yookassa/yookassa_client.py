import msgspec
from app.services.yookassa.models.create_payment import CreatePayment
from app.services.http.http_client import HttpClient
from app.config.settings import get_settings
from app.services.yookassa.models.payment import Payment
import base64
import uuid


settings = get_settings()

class YooKassaClient:
    YOOKASSA_API_URL = "https://api.yookassa.ru/v3"
    
    @classmethod
    async def create_payment(
            cls, payment: CreatePayment, 
            idempotence_key: str = None
    ) -> Payment:
        url = f"{cls.YOOKASSA_API_URL}/payments"
        headers = cls.get_headers()
        if not idempotence_key:
            idempotence_key = str(uuid.uuid4())
        headers["Idempotence-Key"] = idempotence_key

        response = await HttpClient.make_json_request(
            url,
            method="POST",
            type_=Payment,
            json=msgspec.json.decode(msgspec.json.encode(payment)),
            headers=headers
        )
        return response
    
    @classmethod
    def get_headers(cls) -> dict:
        auth_value = f"{settings.yookassa.SHOP_ID}:{settings.yookassa.SECRET_KEY}"
        auth_encoded = base64.b64encode(auth_value.encode()).decode()
        return {
            "Authorization": f"Basic {auth_encoded}",
            "Content-Type": "application/json"
        }
