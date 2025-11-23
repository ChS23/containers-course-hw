from __future__ import annotations

from typing import Annotated, TYPE_CHECKING

from advanced_alchemy.service import FilterTypeT
from litestar import Controller, get, post, delete, patch

from app.lib.deps import create_service_dependencies
from app.domain.speakers.services import SpeakerService
from app.domain.speakers.schemas import CreateSpeaker, SpeakerItem, UpdateSpeaker

if TYPE_CHECKING:
    from advanced_alchemy.service.pagination import OffsetPagination
    from litestar.params import Dependency, Parameter


class SpeakerController(Controller):
    tags = ["Speakers"]
    dependencies = create_service_dependencies(
        SpeakerService,
        key="speaker_service"
    )

    @get("/speakers", operation_id="get_speakers")
    async def get_speakers(
            self,
            speaker_service: SpeakerService,
            filters: Annotated[list[FilterTypeT], Dependency(skip_validation=True)],
    ) -> OffsetPagination[SpeakerItem]:
        results, total = await speaker_service.list_and_count(*filters)
        return speaker_service.to_schema(
            data=results,
            total=total,
            schema_type=SpeakerItem,
            filters=filters
        )

    @post("/speakers", operation_id="create_speaker")
    async def create_speaker(
        self,
        speaker_service: SpeakerService,
        data: CreateSpeaker
    ) -> SpeakerItem:
        obj = data.to_dict()
        db_obj = await speaker_service.create(obj)
        return speaker_service.to_schema(
            data=db_obj,
            schema_type=SpeakerItem
        )

    @patch("/speakers/{speaker_id:int}", operation_id="update_speaker")
    async def update_speaker(
        self,
        data: UpdateSpeaker,
        speaker_service: SpeakerService,
        speaker_id: Annotated[int, Parameter(title="Speaker ID", description="ID of the speaker to update")]
    ) -> SpeakerItem:
        db_obj = await speaker_service.update(
            item_id=speaker_id,
            data=data.to_dict(),
        )
        return speaker_service.to_schema(
            data=db_obj,
            schema_type=SpeakerItem
        )

    @delete("/speakers/{speaker_id:int}", operation_id="delete_speaker")
    async def delete_speaker(
        self,
        speaker_service: SpeakerService,
        speaker_id: Annotated[int, Parameter(title="Speaker ID", description="ID of the speaker to delete")]
    ) -> None:
        _ = await speaker_service.delete(speaker_id)
