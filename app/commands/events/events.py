import json
from typing import List
from app.models.event import Agenda, Event, Faq, Location, State
from app.schemas.event import (
    EventCreateSchema,
    EventSchema,
)
from .errors import (
    EventAlreadyExistsError,
    EventNotFoundError,
    AgendaEmptyError,
    AgendaEmptySpaceError,
    AgendaOverlapError,
    AgendaTooLargeError,
    EventNotBorradorError,
)
from app.repositories.event import (
    EventRepository,
    Search,
)
from app.config.logger import setup_logger
from datetime import time
import datetime

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
        agenda = [
            Agenda(
                time_init=element.time_init,
                time_end=element.time_end,
                owner=element.owner,
                title=element.title,
                description=element.description,
            )
            for element in self.event_data.agenda
        ]

        faq = [
            Faq(
                question=element.question,
                answer=element.answer,
            )
            for element in self.event_data.FAQ
        ]

        event = Event.new(
            name=self.event_data.name,
            description=self.event_data.description,
            location=location,
            type=self.event_data.type,
            images=self.event_data.images,
            preview_image=self.event_data.preview_image,
            date=self.event_data.date,
            organizer=self.event_data.organizer,
            start_time=self.event_data.start_time,
            end_time=self.event_data.end_time,
            agenda=agenda,
            vacants=self.event_data.vacants,
            vacants_left=self.event_data.vacants,
            FAQ=faq,
        )
        self.verify_agenda(agenda, event.end_time)
        already_exists = self.event_repository.event_exists(event.id)
        if already_exists:
            raise EventAlreadyExistsError
        event = self.event_repository.add_event(event)

        return EventSchema.from_model(event)

    def verify_agenda(self, agenda: List[Agenda], end_time: str):
        if len(agenda) == 0:
            raise AgendaEmptyError
        for i in range(1, len(agenda)):
            if time.fromisoformat(agenda[i - 1].time_end) < time.fromisoformat(
                agenda[i].time_init
            ):
                raise AgendaEmptySpaceError
            if time.fromisoformat(agenda[i - 1].time_end) > time.fromisoformat(
                agenda[i].time_init
            ):
                raise AgendaOverlapError
        for element in agenda:
            if time.fromisoformat(element.time_end) > end_time:
                raise AgendaTooLargeError


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
        events_with_finished = self.check_finished(events)
        events_ordered = sorted(
            events_with_finished, key=lambda h: (h.vacants), reverse=False
        )
        return list(map(EventSchema.from_model, events_ordered))

    def check_finished(self, events: List[Event]) -> List[Event]:
        now = datetime.datetime.now().date()
        time = datetime.datetime.now().time()
        new_events = []
        for event in events:
            if event.date < now or (event.date == now and event.end_time < time):
                event = self.event_repository.update_state_event(
                    event.id, State.Finalizado
                )
            new_events.append(event)
        return new_events


class PublishEventCommand:
    def __init__(self, event_repository: EventRepository, _id: str):
        self.event_repository = event_repository
        self.id = _id

    def execute(self) -> EventSchema:
        exists = self.event_repository.event_exists(self.id)
        if not exists:
            raise EventNotFoundError
        event = self.event_repository.get_event(self.id)
        if event.state == State.Borrador:
            event = self.event_repository.update_state_event(self.id, State.Publicado)
        else:
            raise EventNotBorradorError
        return EventSchema.from_model(event)
