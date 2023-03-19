from app.utils.error import TicketAppError


class BusinessError(TicketAppError):
    def __init__(self, message):
        super().__init__(message)
