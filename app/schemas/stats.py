from __future__ import annotations
from pydantic import BaseModel, Field
from app.models.stat import (
    EventBookingsByHourStat,
    AppStats,
    OrganizerStat,
    VerifiedBookingStat,
)


class EventBookingsByHourStatSchema(BaseModel):
    time: str = Field(..., min_length=13, max_length=13)
    bookings: int = Field(..., example=0)

    @classmethod
    def from_model(cls, stat: EventBookingsByHourStat) -> EventBookingsByHourStatSchema:
        return EventBookingsByHourStatSchema(
            time=stat.time,
            bookings=stat.bookings,
        )


class EventStatesStatSchema(BaseModel):
    Borrador: int = Field(..., example=0)
    Publicado: int = Field(..., example=0)
    Finalizado: int = Field(..., example=0)
    Cancelado: int = Field(..., example=0)
    Suspendido: int = Field(..., example=0)


class OrganizerStatSchema(BaseModel):
    name: str = Field(..., example="Organizer")
    events: int = Field(..., example=0)

    @classmethod
    def from_model(cls, stat: OrganizerStat) -> OrganizerStatSchema:
        return OrganizerStatSchema(
            name=stat.name,
            events=stat.events,
        )


class VerifiedBookingStatSchema(BaseModel):
    date: str = Field(...)
    bookings: int = Field(..., example=0)

    @classmethod
    def from_model(cls, stat: VerifiedBookingStat) -> VerifiedBookingStatSchema:
        return VerifiedBookingStatSchema(
            date=stat.date,
            bookings=stat.bookings,
        )


class AppStatsSchema(BaseModel):
    event_states: EventStatesStatSchema
    top_organizers: list[OrganizerStatSchema]
    verified_bookings: list[VerifiedBookingStatSchema]

    @classmethod
    def from_model(cls, stats: AppStats) -> AppStatsSchema:
        event_states = EventStatesStatSchema(
            Borrador=stats.event_states.Borrador,
            Publicado=stats.event_states.Publicado,
            Finalizado=stats.event_states.Finalizado,
            Cancelado=stats.event_states.Cancelado,
            Suspendido=stats.event_states.Suspendido,
        )
        top_organizers = [
            OrganizerStatSchema.from_model(organizer)
            for organizer in stats.top_organizers
        ]
        verified_bookings = [
            VerifiedBookingStatSchema.from_model(booking)
            for booking in stats.verified_bookings
        ]
        return AppStatsSchema(
            event_states=event_states,
            top_organizers=top_organizers,
            verified_bookings=verified_bookings,
        )


class StatParams(BaseModel):
    start_date: str = Field(..., min_length=10, max_length=10)
    end_date: str = Field(..., min_length=10, max_length=10)
