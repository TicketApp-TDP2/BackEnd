from app.repositories.config import db
from abc import ABC, abstractmethod
from app.models.booking import Booking
from app.repositories.errors import BookingNotFoundError


class BookingRepository(ABC):
    @abstractmethod
    def add_booking(self, booking: Booking) -> Booking:
        pass

    @abstractmethod
    def booking_exists(self, experience_id: str, reserver_id: str, date: str) -> bool:
        pass

    @abstractmethod
    def get_bookings_by_reserver(self, reserver_id: str) -> list[Booking]:
        pass

    @abstractmethod
    def get_booking(self, booking_id: str) -> Booking:
        pass

    @abstractmethod
    def verify_booking(self, booking_id: str) -> Booking:
        pass


class PersistentBookingRepository(BookingRepository):
    def __init__(self):
        COLLECTION_NAME = "Bookings"
        self.bookings = db[COLLECTION_NAME]

    def add_booking(self, booking: Booking) -> Booking:
        data = self.__serialize_booking(booking)
        self.bookings.insert_one(data)
        return booking

    def booking_exists(self, event_id: str, reserver_id: str) -> bool:
        booking = self.bookings.find_one(
            {'event_id': event_id, 'reserver_id': reserver_id}
        )
        return booking is not None

    def get_bookings_by_reserver(self, reserver_id: str) -> list[Booking]:
        bookings = self.bookings.find({'reserver_id': reserver_id})
        return [self.__deserialize_booking(booking) for booking in bookings]

    def get_booking(self, booking_id: str) -> Booking:
        booking = self.bookings.find_one({'_id': booking_id})
        if booking is None:
            raise BookingNotFoundError
        return self.__deserialize_booking(booking)

    def verify_booking(self, booking_id: str) -> Booking:
        booking = self.get_booking(booking_id)
        booking.verified = True
        data = self.__serialize_booking(booking)
        self.bookings.update_one({'_id': booking_id}, {'$set': data})
        return booking

    def __serialize_booking(self, booking: Booking) -> dict:
        serialized = {
            '_id': booking.id,
            "event_id": booking.event_id,
            "reserver_id": booking.reserver_id,
            "verified": booking.verified,
        }

        return serialized

    def __deserialize_booking(self, data: dict) -> Booking:
        return Booking(
            id=data['_id'],
            event_id=data['event_id'],
            reserver_id=data['reserver_id'],
            verified=data['verified'],
        )
