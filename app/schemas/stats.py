from __future__ import annotations
from pydantic import BaseModel, Field
from app.models.stat import EventBookingsByHourStat, AppStats


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


class AppStatsSchema(BaseModel):
    event_states: EventStatesStatSchema

    @classmethod
    def from_model(cls, stats: AppStats) -> AppStatsSchema:
        event_states = EventStatesStatSchema(
            Borrador=stats.event_states.Borrador,
            Publicado=stats.event_states.Publicado,
            Finalizado=stats.event_states.Finalizado,
            Cancelado=stats.event_states.Cancelado,
            Suspendido=stats.event_states.Suspendido,
        )
        return AppStatsSchema(event_states=event_states)


class StatParams(BaseModel):
    start_date: str = Field(..., min_length=10, max_length=10)
    end_date: str = Field(..., min_length=10, max_length=10)
