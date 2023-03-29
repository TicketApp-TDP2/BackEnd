from app.models.errors import BusinessError


class EventNotFoundError(BusinessError):
    def __init__(self):
        msg = "Event not found"
        super().__init__(msg)


class EventAlreadyExistsError(BusinessError):
    def __init__(self):
        msg = "Event already exists"
        super().__init__(msg)
