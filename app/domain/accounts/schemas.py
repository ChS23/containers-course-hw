import datetime

from app.lib.schema import CamelizedBaseStruct


class UserItem(CamelizedBaseStruct):
    id: int
    email: str
    first_name: str
    last_name: str
    is_pro: bool
    pro_expired_at: datetime.datetime | None
