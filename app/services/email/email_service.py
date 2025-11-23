from __future__ import annotations

from typing import TYPE_CHECKING
import aiosmtplib
from email.message import EmailMessage
import structlog

from app.config.settings import get_settings
from app.db.models.event_ticket import EventTicket, EventTicketStatus

if TYPE_CHECKING:
    from app.db.models.event import Event
    from app.db.models.user import User

settings = get_settings()
logger = structlog.get_logger()

class EmailService:
    _smtp: aiosmtplib.SMTP | None = None
    logger = logger.bind(service="email_service")

    @classmethod
    async def get_smtp(cls) -> aiosmtplib.SMTP:
        """Получение или создание SMTP соединения"""
        if cls._smtp is None or not cls._smtp.is_connected:
            cls._smtp = aiosmtplib.SMTP(
                hostname=settings.email.SMTP_HOST,
                port=settings.email.SMTP_PORT,
                use_tls=True
            )
            await cls._smtp.connect()
            await cls._smtp.login(
                settings.email.SMTP_USER,
                settings.email.SMTP_PASSWORD
            )
        return cls._smtp

    @classmethod
    async def close_smtp(cls) -> None:
        """Закрытие SMTP соединения"""
        if cls._smtp and cls._smtp.is_connected:
            await cls._smtp.quit()
            cls._smtp = None

    @classmethod
    async def send_ticket_to_email(cls, ticket: EventTicket) -> None:
        """Отправка билета на email"""
        event = ticket.event
        user = ticket.user
        
        # Создаем HTML шаблон письма
        html = cls._get_ticket_template(event, user, ticket)
        
        # Создаем сообщение
        message = EmailMessage()
        message["Subject"] = f"Билет на мероприятие \"{event.title}\""
        message["From"] = settings.email.SMTP_USER
        message["To"] = user.email
        message.set_content(html, subtype="html")
        
        # Получаем SMTP соединение и отправляем
        smtp = await cls.get_smtp()
        try:
            await smtp.send_message(message)
            await cls.logger.ainfo(
                "Email sent",
                ticket_id=ticket.id,
                event_id=event.id,
                user_id=user.id,
                email=user.email
            )
        except Exception as e:
            await cls.logger.aerror(
                "Failed to send email",
                ticket_id=ticket.id,
                event_id=event.id,
                user_id=user.id,
                email=user.email,
                error=str(e)
            )
            # Если произошла ошибка, закрываем соединение
            await cls.close_smtp()
            raise e

    @classmethod
    def _get_ticket_template(cls, event: Event, user: User, ticket: EventTicket) -> str:
        """Генерация HTML шаблона письма"""
        status_text = {
            EventTicketStatus.WAITING_PAYMENT: "Ожидает оплаты",
            EventTicketStatus.PAID: "Оплачен",
            EventTicketStatus.REFUNDED: "Возвращен"
        }[ticket.status]

        status_color = '#22c55e' if ticket.status == EventTicketStatus.PAID else '#dc2626'

        return f"""
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="utf-8">
            </head>
            <body style="margin: 0; padding: 0; background-color: #f3f4f6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
                <table cellpadding="0" cellspacing="0" width="100%" style="background-color: #f3f4f6;">
                    <tr>
                        <td align="center" style="padding: 40px 20px;">
                            <!-- Основной контейнер -->
                            <table cellpadding="0" cellspacing="0" width="600" style="background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                                <!-- Заголовок -->
                                <tr>
                                    <td style="background-color: #1e293b; padding: 40px 30px; text-align: center;">
                                        <table width="100%" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td style="text-align: center;">
                                                    <div style="color: #94a3b8; text-transform: uppercase; letter-spacing: 2px; font-size: 14px; margin-bottom: 12px;">Электронный билет</div>
                                                    <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 700;">{event.title}</h1>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>

                                <tr>
                                    <td style="padding: 40px 30px;">
                                        <!-- Статус билета -->
                                        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 30px;">
                                            <tr>
                                                <td align="center">
                                                    <span style="background-color: {status_color}; color: white; padding: 8px 16px; border-radius: 9999px; font-size: 14px; font-weight: 500;">{status_text}</span>
                                                </td>
                                            </tr>
                                        </table>

                                        <!-- Основная информация -->
                                        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 30px;">
                                            <tr>
                                                <td>
                                                    <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px;">
                                                        <table width="100%" cellpadding="0" cellspacing="0">
                                                            <tr>
                                                                <td>
                                                                    <div style="color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">Номер билета</div>
                                                                    <div style="color: #0f172a; font-size: 18px; font-weight: 600;">#{ticket.id}</div>
                                                                </td>
                                                                <td align="right">
                                                                    <div style="color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">Стоимость</div>
                                                                    <div style="color: #0f172a; font-size: 18px; font-weight: 600;">{ticket.amount_paid} ₽</div>
                                                                </td>
                                                            </tr>
                                                        </table>
                                                    </div>
                                                </td>
                                            </tr>
                                        </table>

                                        <!-- Детали мероприятия -->
                                        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 30px;">
                                            <tr>
                                                <td>
                                                    <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px;">
                                                        <div style="color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 16px;">Информация о мероприятии</div>
                                                        
                                                        <table width="100%" cellpadding="0" cellspacing="0">
                                                            <tr>
                                                                <td style="padding-bottom: 12px;">
                                                                    <div style="color: #64748b; font-size: 14px;">Дата и время</div>
                                                                    <div style="color: #0f172a; font-size: 16px; font-weight: 500;">{event.event_date.strftime('%d.%m.%Y %H:%M')}</div>
                                                                </td>
                                                            </tr>
                                                            <tr>
                                                                <td>
                                                                    <div style="color: #64748b; font-size: 14px;">Место проведения</div>
                                                                    <div style="color: #0f172a; font-size: 16px; font-weight: 500;">{event.location}</div>
                                                                </td>
                                                            </tr>
                                                        </table>
                                                    </div>
                                                </td>
                                            </tr>
                                        </table>

                                        <!-- Информация о покупателе -->
                                        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 30px;">
                                            <tr>
                                                <td>
                                                    <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px;">
                                                        <div style="color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 16px;">Информация о покупателе</div>
                                                        <div style="color: #0f172a; font-size: 16px; font-weight: 500;">{user.first_name}</div>
                                                    </div>
                                                </td>
                                            </tr>
                                        </table>

                                        {f'''
                                        <!-- Ссылка на чат -->
                                        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 30px;">
                                            <tr>
                                                <td align="center">
                                                    <a href="{event.chat_link}" 
                                                       style="display: inline-block; padding: 14px 32px; background-color: #1e293b; 
                                                              color: white; text-decoration: none; border-radius: 8px;
                                                              font-weight: 500; font-size: 16px;">
                                                        Присоединиться к чату
                                                    </a>
                                                </td>
                                            </tr>
                                        </table>
                                        ''' if event.chat_link and ticket.status == EventTicketStatus.PAID else ''}

                                    </td>
                                </tr>

                                <!-- Подвал -->
                                <tr>
                                    <td style="padding: 24px; text-align: center; background-color: #f8fafc;">
                                        <div style="color: #64748b; font-size: 14px;">Если у вас возникли вопросы, пожалуйста, свяжитесь с нами.</div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
        </html>
        """
        