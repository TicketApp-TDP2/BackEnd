from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import date, time
from typing import List, Optional, Tuple
from app.models.event import Event, Type


class LocationSchema(BaseModel):
    description: str = Field(..., min_length=3)
    lat: float
    lng: float


class EventSchemaBase(BaseModel):
    title: str = Field(..., min_length=3)
    description: str = Field(..., min_length=3)
    location: LocationSchema
    type: Type
    images: List[str] = Field(..., min_length=1)
    preview_image: str = Field(..., min_length=1)
    date: date
    start_time: time
    end_time: time
    organizer: str = Field(..., min_length=3)
    agenda: str = Field(..., min_length=3)  # TO DEFINE
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
            title=event.title,
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
