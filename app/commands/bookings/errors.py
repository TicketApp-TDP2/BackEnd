from app.models.errors import BusinessError


class BookingAlreadyExistsError(BusinessError):
    def __init__(self):
        msg = "Booking already exists"
        super().__init__(msg)


class EventFullError(BusinessError):
    def __init__(self):
        msg = "No more vacants left"
        super().__init__(msg)


class IncorrectEventError(BusinessError):
    def __init__(self):
        msg = "Incorrect Event"
        super().__init__(msg)


class BookingAlreadyVerifiedError(BusinessError):
    def __init__(self):
        msg = "Booking already verified"
        super().__init__(msg)
