import json
from typing import List
from app.models.event import Agenda, Event, Faq, Location, State, Collaborator
from app.schemas.event import EventCreateSchema, EventSchema, EventUpdateSchema
from .errors import (
    EventAlreadyExistsError,
    EventNotFoundError,
    AgendaEmptyError,
    AgendaEmptySpaceError,
    AgendaOverlapError,
    AgendaTooLargeError,
    EventNotBorradorError,
    TooManyImagesError,
    TooManyFaqsError,
    EventCannotBeUpdatedError,
    VacantsCannotBeUpdatedError,
    EventCannotBeSuspendedError,
    EventCannotBeUnSuspendedError,
    CollaboratorNotFoundError,
    EventTimeError,
    AgendaDoesNotEndError,
    TimeCanNotBeUpdatedWithoutAgendaError,
)
from app.repositories.event import (
    EventRepository,
    Search,
)
from app.repositories.organizers import OrganizerRepository
from app.config.logger import setup_logger
from datetime import time
from app.utils.now import getNow

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
        if len(faq) > 30:
            raise TooManyFaqsError

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
            scan_time=self.event_data.scan_time,
            agenda=agenda,
            vacants=self.event_data.vacants,
            vacants_left=self.event_data.vacants,
            FAQ=faq,
        )
        if event.start_time >= event.end_time:
            raise EventTimeError
        verify_agenda(agenda, event.end_time)
        already_exists = self.event_repository.event_exists(event.id)
        if already_exists:
            raise EventAlreadyExistsError
        if len(event.images) > 9:
            raise TooManyImagesError
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
        event_with_finished = self.check_finished(event)

        return EventSchema.from_model(event_with_finished)

    def check_finished(self, event: Event) -> Event:
        now = getNow().date()
        time = getNow().time()
        if event.date < now or (event.date == now and event.end_time < time):
            event = self.event_repository.update_state_event(event.id, State.Finalizado)
        return event


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
        if not self.search.organizer:
            events_ordered = sorted(
                events_with_finished, key=lambda h: (h.vacants), reverse=False
            )
        else:
            events_ordered = sorted(
                events_with_finished,
                key=lambda h: (h.date, h.start_time),
                reverse=False,
            )
        return list(map(EventSchema.from_model, events_ordered))

    def check_finished(self, events: List[Event]) -> List[Event]:
        now = getNow().date()
        time = getNow().time()
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


class CancelEventCommand:
    def __init__(self, event_repository: EventRepository, _id: str):
        self.event_repository = event_repository
        self.id = _id

    def execute(self) -> EventSchema:
        exists = self.event_repository.event_exists(self.id)
        if not exists:
            raise EventNotFoundError
        event = self.event_repository.update_state_event(self.id, State.Cancelado)
        return EventSchema.from_model(event)


class UpdateEventCommand:
    def __init__(
        self,
        event_repository: EventRepository,
        update: EventUpdateSchema,
        id: str,
    ):
        self.event_repository = event_repository
        self.update = update
        self.id = id

    def execute(self) -> EventSchema:
        if self.update.start_time and not self.update.agenda:
            raise TimeCanNotBeUpdatedWithoutAgendaError
        if self.update.end_time and not self.update.agenda:
            raise TimeCanNotBeUpdatedWithoutAgendaError
        event = self.event_repository.get_event(self.id)
        if event.state != State.Borrador and event.state != State.Publicado:
            raise EventCannotBeUpdatedError
        if (
            self.update.vacants
            and self.update.vacants < event.vacants - event.vacants_left
        ):
            raise VacantsCannotBeUpdatedError
        if self.update.location:
            location = Location(
                description=self.update.location.description,
                lat=self.update.location.lat,
                lng=self.update.location.lng,
            )
        if self.update.agenda:
            agenda = [
                Agenda(
                    time_init=element.time_init,
                    time_end=element.time_end,
                    owner=element.owner,
                    title=element.title,
                    description=element.description,
                )
                for element in self.update.agenda
            ]
        if self.update.FAQ:
            faq = [
                Faq(
                    question=element.question,
                    answer=element.answer,
                )
                for element in self.update.FAQ
            ]
            if len(faq) > 30:
                raise TooManyFaqsError
        event = Event(
            id=event.id,
            name=self.update.name if self.update.name else event.name,
            description=self.update.description
            if self.update.description
            else event.description,
            location=location if self.update.location else event.location,
            type=self.update.type if self.update.type else event.type,
            images=self.update.images if self.update.images else event.images,
            preview_image=self.update.preview_image
            if self.update.preview_image
            else event.preview_image,
            date=self.update.date if self.update.date else event.date,
            organizer=event.organizer,
            start_time=self.update.start_time
            if self.update.start_time
            else event.start_time,
            end_time=self.update.end_time if self.update.end_time else event.end_time,
            scan_time=self.update.scan_time
            if self.update.scan_time
            else event.scan_time,
            agenda=agenda if self.update.agenda else event.agenda,
            vacants=self.update.vacants if self.update.vacants else event.vacants,
            vacants_left=(self.update.vacants - (event.vacants - event.vacants_left))
            if self.update.vacants
            else event.vacants_left,
            FAQ=faq if self.update.FAQ else event.FAQ,
            state=event.state,
            verified_vacants=event.verified_vacants,
            collaborators=event.collaborators,
        )
        if event.start_time >= event.end_time:
            raise EventTimeError
        verify_agenda(event.agenda, event.end_time)
        event = self.event_repository.update_event(event)

        return EventSchema.from_model(event)


class SuspendEventCommand:
    def __init__(self, event_repository: EventRepository, _id: str):
        self.event_repository = event_repository
        self.id = _id

    def execute(self) -> EventSchema:
        exists = self.event_repository.event_exists(self.id)
        if not exists:
            raise EventNotFoundError
        event = self.event_repository.get_event(self.id)
        if event.state == State.Publicado:
            event = self.event_repository.update_state_event(self.id, State.Suspendido)
        else:
            raise EventCannotBeSuspendedError
        return EventSchema.from_model(event)


class UnSuspendEventCommand:
    def __init__(self, event_repository: EventRepository, _id: str):
        self.event_repository = event_repository
        self.id = _id

    def execute(self) -> EventSchema:
        exists = self.event_repository.event_exists(self.id)
        if not exists:
            raise EventNotFoundError
        event = self.event_repository.get_event(self.id)
        if event.state == State.Suspendido:
            event = self.event_repository.update_state_event(self.id, State.Publicado)
        else:
            raise EventCannotBeUnSuspendedError
        return EventSchema.from_model(event)


class AddCollaboratorEventCommand:
    def __init__(
        self,
        event_repository: EventRepository,
        organizer_repository: OrganizerRepository,
        _id: str,
        collaborator_email: str,
    ):
        self.event_repository = event_repository
        self.organizer_repository = organizer_repository
        self.id = _id
        self.collaborator_email = collaborator_email

    def execute(self) -> EventSchema:
        exists = self.event_repository.event_exists(self.id)
        if not exists:
            raise EventNotFoundError
        collaborator_exists = self.organizer_repository.organizer_exists_by_email(
            self.collaborator_email
        )
        if not collaborator_exists:
            raise CollaboratorNotFoundError
        collaborator = self.organizer_repository.get_organizer_by_email(
            self.collaborator_email
        )
        event = self.event_repository.get_event(self.id)
        collaborators = event.collaborators
        collaborator = Collaborator(id=collaborator.id, email=collaborator.email)
        if collaborator not in collaborators:
            collaborators.append(collaborator)
        event.collaborators = collaborators
        event = self.event_repository.update_event(event)
        return EventSchema.from_model(event)


class RemoveCollaboratorEventCommand:
    def __init__(
        self,
        event_repository: EventRepository,
        organizer_repository: OrganizerRepository,
        _id: str,
        collaborator_id: str,
    ):
        self.event_repository = event_repository
        self.organizer_repository = organizer_repository
        self.id = _id
        self.collaborator_id = collaborator_id

    def execute(self) -> EventSchema:
        exists = self.event_repository.event_exists(self.id)
        if not exists:
            raise EventNotFoundError
        event = self.event_repository.get_event(self.id)
        collaborators = event.collaborators

        collaborator_exists = self.organizer_repository.organizer_exists(
            self.collaborator_id
        )
        if collaborator_exists:
            collaborator = self.organizer_repository.get_organizer(self.collaborator_id)
            collaborator = Collaborator(id=collaborator.id, email=collaborator.email)
            if collaborator in collaborators:
                collaborators.remove(collaborator)
            event.collaborators = collaborators

        event = self.event_repository.update_event(event)
        return EventSchema.from_model(event)


def verify_agenda(agenda: List[Agenda], end_time: str):
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
    if time.fromisoformat(agenda[-1].time_end) != end_time:
        raise AgendaDoesNotEndError
