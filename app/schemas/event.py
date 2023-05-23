from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import date, time
from typing import List, Optional, Tuple
from app.models.event import Event, Type, State


class SearchEvent(BaseModel):
    lat: Optional[float]
    lng: Optional[float]
    dist: int = Field(default=5_000)
    organizer: Optional[str]
    type: Optional[Type]
    limit: int = Field(default=5000)
    name: Optional[str]
    only_published: Optional[bool]
    not_finished: Optional[bool]


class LocationSchema(BaseModel):
    description: str = Field(..., min_length=3)
    lat: float
    lng: float


class FaqSchema(BaseModel):
    question: str = Field(..., min_length=3)
    answer: str = Field(..., min_length=3)


class CollaboratorSchema(BaseModel):
    id: str = Field(..., min_length=3)
    email: str = Field(..., min_length=3)


class AgendaSchema(BaseModel):
    time_init: str = Field(..., min_length=3)
    time_end: str = Field(..., min_length=3)
    owner: str = Field(..., min_length=3)
    title: str = Field(..., min_length=3)
    description: str = Field(..., min_length=3)


class EventSchemaBase(BaseModel):
    name: str = Field(..., min_length=3)
    description: str = Field(..., min_length=3)
    location: LocationSchema
    type: Type
    images: List[str] = Field(..., min_length=1)
    preview_image: str = Field(..., min_length=1)
    date: date
    start_time: time
    end_time: time
    scan_time: int = Field(..., ge=1, le=12)
    organizer: str = Field(..., min_length=3)
    agenda: List[AgendaSchema]
    vacants: int = Field(..., ge=1)
    FAQ: List[FaqSchema]


class EventCreateSchema(EventSchemaBase):
    pass


class EventUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=3)
    description: Optional[str] = Field(None, min_length=3)
    location: Optional[LocationSchema]
    type: Optional[Type]
    images: Optional[List[str]] = Field(None, min_length=1)
    preview_image: Optional[str] = Field(None, min_length=1)
    date: Optional[date]
    start_time: Optional[time]
    end_time: Optional[time]
    scan_time: Optional[int] = Field(None, ge=1, le=12)
    agenda: Optional[List[AgendaSchema]]
    vacants: Optional[int] = Field(None, ge=1)
    FAQ: Optional[List[FaqSchema]]


class EventSchema(EventSchemaBase):
    id: str = Field(..., min_length=1)
    vacants_left: int = Field(..., ge=0)
    state: State
    verified_vacants: int
    collaborators: List[CollaboratorSchema]

    @classmethod
    def from_model(cls, event: Event) -> EventSchema:
        location = LocationSchema(
            description=event.location.description,
            lat=event.location.lat,
            lng=event.location.lng,
        )
        agenda = [
            AgendaSchema(
                time_init=element.time_init,
                time_end=element.time_end,
                owner=element.owner,
                title=element.title,
                description=element.description,
            )
            for element in event.agenda
        ]

        faq = [
            FaqSchema(
                question=element.question,
                answer=element.answer,
            )
            for element in event.FAQ
        ]

        collaborators = [
            CollaboratorSchema(
                id=element.id,
                email=element.email,
            )
            for element in event.collaborators
        ]

        return EventSchema(
            name=event.name,
            description=event.description,
            location=location,
            type=Type(event.type),
            images=event.images,
            preview_image=event.preview_image,
            date=event.date,
            start_time=event.start_time,
            end_time=event.end_time,
            scan_time=event.scan_time,
            organizer=event.organizer,
            agenda=agenda,
            vacants=event.vacants,
            vacants_left=event.vacants_left,
            FAQ=faq,
            id=event.id,
            state=State(event.state),
            verified_vacants=event.verified_vacants,
            collaborators=collaborators,
        )
