from __future__ import annotations

from typing import Annotated, TYPE_CHECKING

from advanced_alchemy.service import FilterTypeT
from litestar import Controller, get, post, delete, patch

from app.lib.deps import create_service_dependencies
from app.domain.matireals.services import EventMaterialService
from app.domain.matireals.schemas import CreateEventMaterial, EventMaterialItem, UpdateEventMaterial

if TYPE_CHECKING:
    from advanced_alchemy.service.pagination import OffsetPagination
    from litestar.params import Dependency, Parameter


class EventMaterialController(Controller):
    tags = ["Event Materials"]
    dependencies = create_service_dependencies(
        EventMaterialService,
        key="event_material_service"
    )

    @get("/materials", operation_id="get_event_materials")
    async def get_event_materials(
            self,
            event_material_service: EventMaterialService,
            filters: Annotated[list[FilterTypeT], Dependency(skip_validation=True)],
    ) -> OffsetPagination[EventMaterialItem]:
        results, total = await event_material_service.list_and_count(*filters)
        return event_material_service.to_schema(
            data=results,
            total=total,
            schema_type=EventMaterialItem,
            filters=filters
        )

    @post("/materials", operation_id="create_event_material")
    async def create_event_material(
        self,
        event_material_service: EventMaterialService,
        data: CreateEventMaterial
    ) -> EventMaterialItem:
        obj = data.to_dict()
        db_obj = await event_material_service.create(obj)
        return event_material_service.to_schema(
            data=db_obj,
            schema_type=EventMaterialItem
        )

    @patch("/materials/{material_id:int}", operation_id="update_event_material")
    async def update_event_material(
        self,
        data: UpdateEventMaterial,
        event_material_service: EventMaterialService,
        event_material_id: Annotated[int, Parameter(title="Event Material ID", description="ID of the event material to update")]
    ) -> EventMaterialItem:
        db_obj = await event_material_service.update(
            item_id=event_material_id,
            data=data.to_dict(),
        )
        return event_material_service.to_schema(
            data=db_obj,
            schema_type=EventMaterialItem
        )

    @delete("/materials/{material_id:int}", operation_id="delete_event_material")
    async def delete_event_material(
        self,
        event_material_service: EventMaterialService,
        event_material_id: Annotated[int, Parameter(title="Event Material ID", description="ID of the event material to delete")]
    ) -> None:
        _ = await event_material_service.delete(event_material_id)
