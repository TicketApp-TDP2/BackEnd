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
from app.schemas.stats import EventBookingsByHourStatSchema
from app.utils.now import getNow

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
            verified_time="Not_verified",
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
        now = getNow().date()
        time = getNow().time()
        if event.date < now or (event.date == now and event.end_time < time):
            raise EventFinishedError
        self.event_repository.update_vacants_left_event(
            event.id, event.vacants_left - 1
        )
        booking = self.booking_repository.add_booking(booking)

        return BookingSchema.from_model(booking)


class GetBookingsByReserverCommand:
    def __init__(
        self,
        booking_repository: BookingRepository,
        event_repository: EventRepository,
        reserver_id: str,
    ):
        self.booking_repository = booking_repository
        self.reserver_id = reserver_id
        self.event_repository = event_repository

    def execute(self) -> List[BookingSchema]:
        bookings = self.booking_repository.get_bookings_by_reserver(self.reserver_id)
        events_ids = [booking.event_id for booking in bookings]
        events_ids = [
            event.id
            for event in self.event_repository.get_events_by_id_with_date_filter(
                events_ids
            )
        ]
        return_bookings = [
            booking for booking in bookings if booking.event_id in events_ids
        ]
        return [BookingSchema.from_model(booking) for booking in return_bookings]


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


class GetBookingsByEventCommand:
    def __init__(self, booking_repository: BookingRepository, event_id: str):
        self.booking_repository = booking_repository
        self.event_id = event_id

    def execute(self) -> List[BookingSchema]:
        bookings = self.booking_repository.get_bookings_by_event(self.event_id)
        return [BookingSchema.from_model(booking) for booking in bookings]


class GetBookingsByEventVerifiedCommand:
    def __init__(self, booking_repository: BookingRepository, event_id: str):
        self.booking_repository = booking_repository
        self.event_id = event_id

    def execute(self) -> List[BookingSchema]:
        bookings = self.booking_repository.get_bookings_by_event_verified(self.event_id)
        sorted_bookings = sorted(bookings, key=lambda x: x.verified_time)
        return [BookingSchema.from_model(booking) for booking in sorted_bookings]


class GetBookingsByHourCommand:
    def __init__(self, booking_repository: BookingRepository, event_id: str):
        self.booking_repository = booking_repository
        self.event_id = event_id

    def execute(self) -> List[EventBookingsByHourStatSchema]:
        stats = self.booking_repository.get_bookings_by_hour(self.event_id)
        sorted_stats = sorted(stats, key=lambda x: x.time)
        return [EventBookingsByHourStatSchema.from_model(stat) for stat in sorted_stats]
