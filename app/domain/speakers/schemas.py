import msgspec

from app.lib.schema import CamelizedBaseStruct


class CreateSpeaker(CamelizedBaseStruct):
    name: str | msgspec.UnsetType = msgspec.UNSET
    description: str | None | msgspec.UnsetType = msgspec.UNSET
    user_id: int | msgspec.UnsetType = msgspec.UNSET
    contacts: str | None | msgspec.UnsetType = msgspec.UNSET


class SpeakerItem(CamelizedBaseStruct):
    id: int
    name: str
    description: str | None
    contacts: str | None
    user_id: int | None


class UpdateSpeaker(CamelizedBaseStruct):
    name: str | None
    description: str | None
    contacts: str | None
    user_id: int | None
    