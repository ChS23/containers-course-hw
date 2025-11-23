from __future__ import annotations

from http.client import HTTPException
from typing import Annotated, TYPE_CHECKING

from advanced_alchemy.service import FilterTypeT
from litestar import Controller, get, post, delete
from litestar.params import Parameter

from app.lib.deps import create_service_dependencies
from app.domain.events.services import EventService
from app.db.models import Event
from app.domain.events.schemas import EventItem, CreateEvent

if TYPE_CHECKING:
    from advanced_alchemy.service.pagination import OffsetPagination
    from litestar.params import Dependency, Parameter


class EventController(Controller):
    path = "/events"
    tags = ["Events"]
    dependencies = create_service_dependencies(
        EventService,
        key="event_service",
        load=[
            Event.speakers,
            Event.materials,
            Event.registrations
        ]
    )

    @get(path="/", operation_id="get_events")
    async def get_events(
            self,
            event_service: EventService,
            filters: Annotated[list[FilterTypeT], Dependency(skip_validation=True)],
    ) -> OffsetPagination[EventItem]:
        results, total = await event_service.list_and_count(*filters)
        return event_service.to_schema(
            data=results,
            total=total,
            schema_type=EventItem,
            filters=filters
        )

    @get("/slug/{slug:str}", operation_id="get_event_by_slug")
    async def get_event_by_slug(
        self,
        event_service: EventService,
        slug: Annotated[str, Parameter(title="Event Slug", description="The slug of the event to retrieve")]
    ) -> EventItem:
        result = await event_service.get_one_or_none(slug=slug)
        if not result:
            raise HTTPException(status_code=404, detail="Event not found")
        return event_service.to_schema(
            data=result,
            schema_type=EventItem
        )
    
    @get("/{event_id:int}", operation_id="get_event")
    async def get_event(
        self,
        event_service: EventService,
        event_id: Annotated[int, Parameter(title="Event ID", description="The ID of the event to retrieve")]
    ) -> EventItem:
        result = await event_service.get_one_or_none(id=event_id)
        if not result:
            raise HTTPException(status_code=404, detail="Event not found")
        return event_service.to_schema(
            data=result,
            schema_type=EventItem
        )

    @post(path="/", operation_id="create_event")
    async def create_event(
        self,
        event_service: EventService,
        data: CreateEvent
    ) -> EventItem:
        obj = data.to_dict()
        db_obj = await event_service.create(obj)
        return event_service.to_schema(
            data=db_obj,
            schema_type=EventItem
        )

    @delete(path="/{event_id:int}", operation_id="delete_event")
    async def delete_event(
        self,
        event_service: EventService,
        event_id: Annotated[int, Parameter(title="Event ID", description="The ID of the event to delete")]
    ) -> None:
        _ = await event_service.delete(event_id)
