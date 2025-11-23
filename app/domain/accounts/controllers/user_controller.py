from __future__ import annotations

from typing import Annotated, TYPE_CHECKING

from advanced_alchemy.service import FilterTypeT
from litestar import Controller, get

from app.lib.deps import create_service_dependencies
from app.domain.accounts.services import UserService
from app.db.models import User
from app.domain.accounts.schemas import UserItem

if TYPE_CHECKING:
    from advanced_alchemy.service.pagination import OffsetPagination
    from litestar.params import Dependency


class UserController(Controller):
    tags = ["Users"]
    dependencies = create_service_dependencies(
        UserService,
        key="user_service",
        load=[
            User.tickets,
            User.pro_subscriptions,
            User.speaker
        ]
    )

    @get("/users", operation_id="get_users")
    async def get_users(
            self,
            user_service: UserService,
            filters: Annotated[list[FilterTypeT], Dependency(skip_validation=True)],
    ) -> OffsetPagination[UserItem]:
        results, total = await user_service.list_and_count(*filters)
        return user_service.to_schema(
            data=results,
            total=total,
            schema_type=UserItem,
            filters=filters
        )
    