from app.utils.error import TicketAppError


class RepositoryError(TicketAppError):
    def __init__(self, message):
        super().__init__(message)


class UserNotFoundError(RepositoryError):
    def __init__(self):
        msg = "User not found"
        super().__init__(msg)


class OrganizerNotFoundError(RepositoryError):
    def __init__(self):
        msg = "Organizer not found"
        super().__init__(msg)


class EventNotFoundError(RepositoryError):
    def __init__(self):
        msg = "Event not found"
        super().__init__(msg)


class BookingNotFoundError(RepositoryError):
    def __init__(self):
        msg = "Booking not found"
        super().__init__(msg)
