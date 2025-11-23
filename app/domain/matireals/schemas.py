import msgspec

from app.lib.schema import CamelizedBaseStruct


class CreateEventMaterial(CamelizedBaseStruct):
    title: str | msgspec.UnsetType = msgspec.UNSET
    url: str | msgspec.UnsetType = msgspec.UNSET
    is_pro_only: bool | msgspec.UnsetType = msgspec.UNSET
    event_id: int | msgspec.UnsetType = msgspec.UNSET


class EventMaterialItem(CamelizedBaseStruct):
    id: int
    title: str
    url: str
    is_pro_only: bool
    event_id: int


class UpdateEventMaterial(CamelizedBaseStruct):
    title: str | None
    url: str | None
    is_pro_only: bool | None
    