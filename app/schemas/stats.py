from __future__ import annotations
from pydantic import BaseModel, Field
from app.models.stat import (
    EventBookingsByHourStat,
    AppStats,
    OrganizerStat,
    TopOrganizersStat,
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


class TopOrganizersStatSchema(BaseModel):
    organizers: list[OrganizerStatSchema]

    @classmethod
    def from_model(cls, stat: TopOrganizersStat) -> TopOrganizersStatSchema:
        organizers = [
            OrganizerStatSchema.from_model(organizer) for organizer in stat.organizers
        ]
        return TopOrganizersStatSchema(organizers=organizers)


class AppStatsSchema(BaseModel):
    event_states: EventStatesStatSchema
    top_organizers: TopOrganizersStatSchema

    @classmethod
    def from_model(cls, stats: AppStats) -> AppStatsSchema:
        event_states = EventStatesStatSchema(
            Borrador=stats.event_states.Borrador,
            Publicado=stats.event_states.Publicado,
            Finalizado=stats.event_states.Finalizado,
            Cancelado=stats.event_states.Cancelado,
            Suspendido=stats.event_states.Suspendido,
        )
        top_organizers = TopOrganizersStatSchema.from_model(stats.top_organizers)
        return AppStatsSchema(event_states=event_states, top_organizers=top_organizers)


class StatParams(BaseModel):
    start_date: str = Field(..., min_length=10, max_length=10)
    end_date: str = Field(..., min_length=10, max_length=10)
