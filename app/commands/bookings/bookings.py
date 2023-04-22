from app.schemas.bookings import BookingCreateSchema, BookingSchema
from app.models.booking import Booking

from .errors import (
    BookingAlreadyExistsError,
    EventFullError,
    IncorrectEventError,
    BookingAlreadyVerifiedError,
    EventNotPublishedError,
    EventFinishedError,
)
from app.repositories.bookings import (
    BookingRepository,
)
from app.repositories.event import EventRepository
from app.config.logger import setup_logger
import uuid
from typing import List
from app.schemas.event import State
import datetime

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
        if event.state != State.Publicado:
            raise EventNotPublishedError
        now = datetime.datetime.now().date()
        time = datetime.datetime.now().time()
        if event.date < now or (event.date == now and event.end_time < time):
            raise EventFinishedError
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


class VerifyBookingCommand:
    def __init__(
        self,
        booking_repository: BookingRepository,
        event_repository: EventRepository,
        booking_id: str,
        event_id: str,
    ):
        self.booking_repository = booking_repository
        self.booking_id = booking_id
        self.event_id = event_id
        self.event_repository = event_repository

    def execute(self) -> BookingSchema:
        booking = self.booking_repository.get_booking(self.booking_id)
        if booking.event_id != self.event_id:
            raise IncorrectEventError
        if booking.verified:
            raise BookingAlreadyVerifiedError
        booking = self.booking_repository.verify_booking(self.booking_id)
        event = self.event_repository.get_event(self.event_id)
        self.event_repository.update_verified_vacants(
            self.event_id, event.verified_vacants + 1
        )

        return BookingSchema.from_model(booking)
