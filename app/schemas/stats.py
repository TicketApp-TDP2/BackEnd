from __future__ import annotations
from pydantic import BaseModel, Field
from app.models.stat import (
    EventBookingsByHourStat,
    AppStats,
    OrganizerStat,
    VerifiedBookingStat,
    ComplaintsByTimeStat,
    SuspendedEventStat,
    EventByTimeStat,
    EventPublishedByTimeStat,
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
    verified_bookings: int = Field(..., example=0)
    id: str = Field(..., example="1")

    @classmethod
    def from_model(cls, stat: OrganizerStat) -> OrganizerStatSchema:
        return OrganizerStatSchema(
            name=stat.name,
            verified_bookings=stat.verified_bookings,
            id=stat.id,
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


class ComplaintsByTimeStatSchema(BaseModel):
    date: str = Field(...)
    complaints: int = Field(..., example=0)

    @classmethod
    def from_model(cls, stat: ComplaintsByTimeStat) -> ComplaintsByTimeStatSchema:
        return ComplaintsByTimeStatSchema(
            date=stat.date,
            complaints=stat.complaints,
        )


class SuspendedEventStatSchema(BaseModel):
    date: str = Field(...)
    suspended: int = Field(..., example=0)

    @classmethod
    def from_model(cls, stat: SuspendedEventStat) -> SuspendedEventStatSchema:
        return SuspendedEventStatSchema(
            date=stat.date,
            suspended=stat.suspended,
        )


class EventByTimeStatSchema(BaseModel):
    date: str = Field(...)
    events: int = Field(..., example=0)

    @classmethod
    def from_model(cls, stat: EventByTimeStat) -> EventByTimeStatSchema:
        return EventByTimeStatSchema(
            date=stat.date,
            events=stat.events,
        )


class EventPublishedByTimeStatSchema(BaseModel):
    date: str = Field(...)
    events: int = Field(..., example=0)

    @classmethod
    def from_model(
        cls, stat: EventPublishedByTimeStat
    ) -> EventPublishedByTimeStatSchema:
        return EventPublishedByTimeStatSchema(
            date=stat.date,
            events=stat.events,
        )


class AppStatsSchema(BaseModel):
    event_states: EventStatesStatSchema
    top_organizers: list[OrganizerStatSchema]
    verified_bookings: list[VerifiedBookingStatSchema]
    complaints_by_time: list[ComplaintsByTimeStatSchema]
    suspended_by_time: list[SuspendedEventStatSchema]
    events_by_time: list[EventByTimeStatSchema]
    events_published_by_time: list[EventPublishedByTimeStatSchema]

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
        complaints_by_time = [
            ComplaintsByTimeStatSchema.from_model(complaint)
            for complaint in stats.complaints_by_time
        ]
        suspended_by_time = [
            SuspendedEventStatSchema.from_model(suspended)
            for suspended in stats.suspended_by_time
        ]
        events_by_time = [
            EventByTimeStatSchema.from_model(event) for event in stats.events_by_time
        ]
        events_published_by_time = [
            EventPublishedByTimeStatSchema.from_model(event)
            for event in stats.events_published_by_time
        ]
        return AppStatsSchema(
            event_states=event_states,
            top_organizers=top_organizers,
            verified_bookings=verified_bookings,
            complaints_by_time=complaints_by_time,
            suspended_by_time=suspended_by_time,
            events_by_time=events_by_time,
            events_published_by_time=events_published_by_time,
        )


class StatParams(BaseModel):
    start_date: str = Field(..., min_length=10, max_length=10)
    end_date: str = Field(..., min_length=10, max_length=10)
    group_by: str = Field(default="day")
