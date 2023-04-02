from typing import List
from app.models.event import Event, Location
from app.schemas.event import (
    EventCreateSchema,
    EventSchema,
)
from .errors import EventAlreadyExistsError, EventNotFoundError
from app.repositories.event import (
    EventRepository,
    Search,
)
from app.config.logger import setup_logger

logger = setup_logger(__name__)


class CreateEventCommand:
    def __init__(
        self,
        event_repository: EventRepository,
        event: EventCreateSchema,
    ):
        self.event_repository = event_repository
        self.event_data = event

    def execute(self) -> EventSchema:
        location = Location(
            description=self.event_data.location.description,
            lat=self.event_data.location.lat,
            lng=self.event_data.location.lng,
        )
        event = Event.new(
            title=self.event_data.title,
            description=self.event_data.description,
            location=location,
            type=self.event_data.type,
            images=self.event_data.images,
            preview_image=self.event_data.preview_image,
            date=self.event_data.date,
            organizer=self.event_data.organizer,
            start_time=self.event_data.start_time,
            end_time=self.event_data.end_time,
            agenda=self.event_data.agenda,
            vacants=self.event_data.vacants,
            FAQ=self.event_data.FAQ,
        )
        already_exists = self.event_repository.event_exists(event.id)
        if already_exists:
            raise EventAlreadyExistsError
        event = self.event_repository.add_event(event)

        return EventSchema.from_model(event)


class GetEventCommand:
    def __init__(self, event_repository: EventRepository, _id: str):
        self.event_repository = event_repository
        self.id = _id

    def execute(self) -> EventSchema:

        exists = self.event_repository.event_exists(self.id)
        if not exists:
            raise EventNotFoundError
        event = self.event_repository.get_event(self.id)

        return EventSchema.from_model(event)


class SearchEventsCommand:
    def __init__(
        self,
        event_repository: EventRepository,
        search: Search,
    ):
        self.event_repository = event_repository
        self.search = search

    def execute(self) -> List[EventSchema]:
        events = self.event_repository.search_events(self.search)
        return list(map(EventSchema.from_model, events))