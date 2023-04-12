from app.models.errors import BusinessError


class BookingAlreadyExistsError(BusinessError):
    def __init__(self):
        msg = "Booking already exists"
        super().__init__(msg)
