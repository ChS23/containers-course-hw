import datetime

import msgspec

from app.lib.schema import BaseStruct
from app.db.models.event_ticket import EventTicketStatus


class SpeakerItem(BaseStruct):
    id: int
    name: str
    description: str | None


class MaterialItem(BaseStruct):
    id: int
    title: str
    url: str
    is_pro_only: bool


class TicketItem(BaseStruct):
    id: int
    status: EventTicketStatus
    amount_paid: float


class EventItem(BaseStruct):
    id: int
    slug: str
    title: str
    description: str | None
    cover_url: str | None
    price: float
    pro_price: float
    event_date: datetime.datetime
    location: str
    max_participants: int | None
    chat_link: str | None
    speakers: list[SpeakerItem] | None = None
    materials: list[MaterialItem] | None = None
    registrations: list[TicketItem] | None = None


class CreateEvent(BaseStruct):
    title: str | msgspec.UnsetType = msgspec.UNSET
    description: str | None | msgspec.UnsetType = msgspec.UNSET
    cover_url: str | None | msgspec.UnsetType = msgspec.UNSET
    price: float | msgspec.UnsetType = msgspec.UNSET
    pro_price: float | msgspec.UnsetType = msgspec.UNSET
    event_date: datetime.datetime | msgspec.UnsetType = msgspec.UNSET
    location: str | msgspec.UnsetType = msgspec.UNSET
    max_participants: int | None | msgspec.UnsetType = msgspec.UNSET
    chat_link: str | None | msgspec.UnsetType = msgspec.UNSET
