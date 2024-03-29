from app.repositories.config import db
from abc import ABC, abstractmethod
from app.models.booking import Booking
from app.schemas.stats import EventBookingsByHourStat
from app.repositories.errors import BookingNotFoundError
from app.utils.now import getNow
from app.models.stat import VerifiedBookingStat


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

    @abstractmethod
    def get_bookings_by_event(self, event_id: str) -> list[Booking]:
        pass

    @abstractmethod
    def get_bookings_by_event_verified(self, event_id: str) -> list[Booking]:
        pass

    @abstractmethod
    def get_bookings_by_hour(self, event_id: str) -> list[Booking]:
        pass

    @abstractmethod
    def get_verified_bookings_stat(
        self, start_date: str, end_date: str, group_by: str
    ) -> list[VerifiedBookingStat]:
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

    def get_bookings_by_event(self, event_id: str) -> list[Booking]:
        bookings = self.bookings.find({'event_id': event_id})
        return [self.__deserialize_booking(booking) for booking in bookings]

    def get_bookings_by_event_verified(self, event_id: str) -> list[Booking]:
        bookings = self.bookings.find({'event_id': event_id, 'verified': True})
        return [self.__deserialize_booking(booking) for booking in bookings]

    def get_bookings_by_hour(self, event_id: str) -> list[Booking]:
        pipeline = [
            {'$match': {'event_id': event_id}},
            {'$match': {'verified': True}},
            {'$project': {'verified_time': {'$substr': ['$verified_time', 0, 13]}}},
            {'$group': {'_id': '$verified_time', 'count': {'$sum': 1}}},
        ]
        stats = self.bookings.aggregate(pipeline)
        return [self.__deserialize_stat(stat) for stat in stats]

    def get_booking(self, booking_id: str) -> Booking:
        booking = self.bookings.find_one({'_id': booking_id})
        if booking is None:
            raise BookingNotFoundError
        return self.__deserialize_booking(booking)

    def verify_booking(self, booking_id: str) -> Booking:
        booking = self.get_booking(booking_id)
        booking.verified = True
        now = getNow()
        booking.verified_time = now.strftime('%Y-%m-%d %H:%M')
        data = self.__serialize_booking(booking)
        self.bookings.update_one({'_id': booking_id}, {'$set': data})
        return booking

    def get_verified_bookings_stat(
        self, start_date: str, end_date: str, group_by: str
    ) -> list[VerifiedBookingStat]:
        match group_by:
            case "day":
                substr = 10
            case "month":
                substr = 7
            case "year":
                substr = 4
            case _:
                substr = 10
        pipeline = [
            {'$match': {'verified': True}},
            {'$match': {'verified_time': {'$gte': start_date, '$lte': end_date}}},
            {'$project': {'verified_time': {'$substr': ['$verified_time', 0, substr]}}},
            {'$group': {'_id': '$verified_time', 'count': {'$sum': 1}}},
            {'$sort': {'_id': 1}},
        ]
        stats = self.bookings.aggregate(pipeline)
        return [VerifiedBookingStat(stat["_id"], stat["count"]) for stat in stats]

    def __serialize_booking(self, booking: Booking) -> dict:
        serialized = {
            '_id': booking.id,
            "event_id": booking.event_id,
            "reserver_id": booking.reserver_id,
            "verified": booking.verified,
            "verified_time": booking.verified_time,
        }

        return serialized

    def __deserialize_booking(self, data: dict) -> Booking:
        return Booking(
            id=data['_id'],
            event_id=data['event_id'],
            reserver_id=data['reserver_id'],
            verified=data['verified'],
            verified_time=data['verified_time'],
        )

    def __deserialize_stat(self, data: dict) -> EventBookingsByHourStat:
        return EventBookingsByHourStat(
            time=data['_id'],
            bookings=data['count'],
        )
