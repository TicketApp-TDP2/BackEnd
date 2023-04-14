from app.schemas.bookings import BookingCreateSchema, BookingSchema
from app.models.booking import Booking

from .errors import BookingAlreadyExistsError, EventFullError
from app.repositories.bookings import (
    BookingRepository,
)
from app.repositories.event import EventRepository
from app.config.logger import setup_logger
import uuid
from typing import List

logger = setup_logger(__name__)


class CreateBookingCommand:
    def __init__(
        self,
        booking_repository: BookingRepository,
        booking: BookingCreateSchema,
        event_repository: EventRepository,
    ):
        self.booking_repository = booking_repository
        self.booking_data = booking
        self.event_repository = event_repository

    def execute(self) -> BookingSchema:
        booking = Booking(
            event_id=self.booking_data.event_id,
            reserver_id=self.booking_data.reserver_id,
            id=str(uuid.uuid4()),
            verified=False,
        )
        already_exists = self.booking_repository.booking_exists(
            booking.event_id, booking.reserver_id
        )
        if already_exists:
            raise BookingAlreadyExistsError
        event = self.event_repository.get_event(booking.event_id)
        if event.vacants_left == 0:
            raise EventFullError
        self.event_repository.update_vacants_left_event(
            event.id, event.vacants_left - 1
        )
        booking = self.booking_repository.add_booking(booking)

        return BookingSchema.from_model(booking)


class GetBookingsByReserverCommand:
    def __init__(self, booking_repository: BookingRepository, reserver_id: str):
        self.booking_repository = booking_repository
        self.reserver_id = reserver_id

    def execute(self) -> List[BookingSchema]:
        bookings = self.booking_repository.get_bookings_by_reserver(self.reserver_id)
        return [BookingSchema.from_model(booking) for booking in bookings]
