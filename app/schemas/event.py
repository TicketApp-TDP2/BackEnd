from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import date, time
from typing import List, Optional, Tuple
from app.models.event import Event, Type


class SearchEvent(BaseModel):
    lat: Optional[float]
    lng: Optional[float]
    dist: int = Field(default=5_000)
    organizer: Optional[str]
    type: Optional[Type]
    limit: int = Field(default=5)
    name: Optional[str]


class LocationSchema(BaseModel):
    description: str = Field(..., min_length=3)
    lat: float
    lng: float


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
    organizer: str = Field(..., min_length=3)
    agenda: List[Tuple[str, str, str, str, str]]
    vacants: int = Field(..., ge=1)
    FAQ: List[Tuple[str, str]]


class EventCreateSchema(EventSchemaBase):
    pass


class EventSchema(EventSchemaBase):
    id: str = Field(..., min_length=1)

    @classmethod
    def from_model(cls, event: Event) -> EventSchema:
        location = LocationSchema(
            description=event.location.description,
            lat=event.location.lat,
            lng=event.location.lng,
        )

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
            organizer=event.organizer,
            agenda=event.agenda,
            vacants=event.vacants,
            FAQ=event.FAQ,
            id=event.id,
        )
