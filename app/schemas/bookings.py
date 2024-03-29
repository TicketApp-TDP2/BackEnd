from __future__ import annotations
from pydantic import BaseModel, Field
from app.models.booking import Booking


class BookingSchemaBase(BaseModel):
    event_id: str = Field(..., min_length=1)
    reserver_id: str = Field(..., min_length=1)


class BookingCreateSchema(BookingSchemaBase):
    pass


class verifyBookingSchema(BaseModel):
    event_id: str = Field(..., min_length=1)


class BookingSchema(BookingSchemaBase):
    id: str = Field(..., min_length=1)
    verified: bool
    verified_time: str

    @classmethod
    def from_model(cls, booking: Booking) -> BookingSchema:
        return BookingSchema(
            event_id=booking.event_id,
            reserver_id=booking.reserver_id,
            id=booking.id,
            verified=booking.verified,
            verified_time=booking.verified_time,
        )
