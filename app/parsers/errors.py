from app.utils.error import TicketAppError


class ParserError(TicketAppError):
    def __init__(self, message):
        super().__init__(message)


class LocationIncompleteError(ParserError):
    def __init__(self):
        msg = "location_incomplete_in_search"
        super().__init__(msg)
