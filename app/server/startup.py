from app.services.http.http_client import HttpClient
from app.services.email.email_service import EmailService


async def start_http_session():
    HttpClient.inizialize_session()
    # SMTP connection removed - will connect on-demand when sending emails
    # await EmailService.get_smtp()
