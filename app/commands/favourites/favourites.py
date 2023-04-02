from typing import List
from app.commands.events.errors import EventNotFoundError
from app.commands.users.errors import UserNotFoundError
from app.models.favourite import Favourite
from app.models.user import User
from app.repositories.event import EventRepository
from app.schemas.event import EventSchema
from app.schemas.favourite import FavouriteSchema
from app.repositories import (
    UserRepository,
)
from app.config.logger import setup_logger

logger = setup_logger(__name__)


class AddFavouriteCommand:
    def __init__(
        self,
        user_repository: UserRepository,
        event_repository: EventRepository,
        user_id: str,
        favourite: FavouriteSchema,
    ):
        self.user_repository = user_repository
        self.event_repository = event_repository
        self.favourite = favourite
        self.user_id = user_id

    def execute(self) -> None:

        event_id = self.favourite.event_id
        user_id = self.user_id

        favourite = Favourite(user_id=user_id, event_id=event_id)

        user_exists = self.user_repository.user_exists(self.user_id)
        if not user_exists:
            raise UserNotFoundError

        event_exists = self.event_repository.event_exists(event_id)
        if not event_exists:
            raise EventNotFoundError

        self.user_repository.add_favourite(favourite)


class GetFavouritesCommand:
    def __init__(
        self,
        user_repository: UserRepository,
        event_repository: EventRepository,
        user_id: str,
    ):
        self.user_repository = user_repository
        self.event_repository = event_repository
        self.user_id = user_id

    def execute(self) -> List[EventSchema]:
        user: User
        try:
            user = self.user_repository.get_user(self.user_id)
        except Exception:
            raise UserNotFoundError

        events = self.event_repository.get_events_by_id(user.favourites)

        return list(map(lambda x: EventSchema.from_model(x), events))


class DeleteFavouriteCommand:
    def __init__(self, user_repository: UserRepository, user_id: str, event_id: str):
        self.user_repository = user_repository
        self.event_id = event_id
        self.user_id = user_id

    def execute(self) -> None:
        user: User
        try:
            user = self.user_repository.get_user(self.user_id)
        except Exception:
            raise UserNotFoundError

        user.remove_favourite(self.event_id)
        self.user_repository.update_user(user)
