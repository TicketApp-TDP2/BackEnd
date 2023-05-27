from app.models.errors import BusinessError


class BookingAlreadyExistsError(BusinessError):
    def __init__(self):
        msg = "booking_already_exists"
        super().__init__(msg)


class EventFullError(BusinessError):
    def __init__(self):
        msg = "no_more_vacants_left"
        super().__init__(msg)


class IncorrectEventError(BusinessError):
    def __init__(self):
        msg = "incorrect_event"
        super().__init__(msg)


class BookingAlreadyVerifiedError(BusinessError):
    def __init__(self):
        msg = "booking_already_verified"
        super().__init__(msg)


class EventNotPublishedError(BusinessError):
    def __init__(self):
        msg = "event_not_published"
        super().__init__(msg)


class EventFinishedError(BusinessError):
    def __init__(self):
        msg = "event_already_finished"
        super().__init__(msg)


class ComplaintAlreadyExistsError(BusinessError):
    def __init__(self):
        msg = "complaint_already_exists"
        super().__init__(msg)
