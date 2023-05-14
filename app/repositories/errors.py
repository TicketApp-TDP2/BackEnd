from app.utils.error import TicketAppError


class RepositoryError(TicketAppError):
    def __init__(self, message):
        super().__init__(message)


class UserNotFoundError(RepositoryError):
    def __init__(self):
        msg = "user_not_found"
        super().__init__(msg)


class OrganizerNotFoundError(RepositoryError):
    def __init__(self):
        msg = "organizer_not_found"
        super().__init__(msg)


class EventNotFoundError(RepositoryError):
    def __init__(self):
        msg = "event_not_found"
        super().__init__(msg)


class BookingNotFoundError(RepositoryError):
    def __init__(self):
        msg = "booking_not_found"
        super().__init__(msg)


class ComplaintNotFoundError(RepositoryError):
    def __init__(self):
        msg = "complaint_not_found"
        super().__init__(msg)
