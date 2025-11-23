import datetime

import msgspec

from app.lib.schema import CamelizedBaseStruct


# Регистрация не зарегистрированного пользователя
class UnregisteredUserRegistrationSchema(CamelizedBaseStruct):
    email: str
    first_name: str
    last_name: str
    event_id: int
    source: str
    contact_info: str | None | msgspec.UnsetType = msgspec.UNSET


# Регистрация зарегистрированного пользователя с Telegram ID
class RegisteredUserRegistrationSchema(CamelizedBaseStruct):
    user_id: int
    event_id: int
    source: str


class RegistrationResponseSchema(CamelizedBaseStruct):
    payment_url: str
