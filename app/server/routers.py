from __future__ import annotations
from litestar import Router

from typing import TYPE_CHECKING

from app.domain.events.controllers import EventController
from app.domain.speakers.controllers import SpeakerController
from app.domain.matireals.controllers import EventMaterialController
from app.domain.registrations.controllers import RegistrationController
from app.domain.accounts.controllers.user_controller import UserController
from app.domain.payments.controllers.webhook import WebhookController

if TYPE_CHECKING:
    from litestar.types import ControllerRouterHandler


route_handlers: list[ControllerRouterHandler] = [
    EventController,
    SpeakerController,
    EventMaterialController,
    RegistrationController,
    UserController,
    WebhookController
]

api_v1_router = Router(path="/api/v1", route_handlers=route_handlers)

routers_list: list[Router] = [
    api_v1_router
]

__all__ = [
    "routers_list"
]
