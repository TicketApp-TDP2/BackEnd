from app.models.errors import BusinessError


class EventNotFoundError(BusinessError):
    def __init__(self):
        msg = "Event not found"
        super().__init__(msg)


class EventAlreadyExistsError(BusinessError):
    def __init__(self):
        msg = "Event already exists"
        super().__init__(msg)


class AgendaEmptyError(BusinessError):
    def __init__(self):
        msg = "Agenda can not be empty"
        super().__init__(msg)


class AgendaEmptySpaceError(BusinessError):
    def __init__(self):
        msg = "Agenda can not have empty spaces"
        super().__init__(msg)


class AgendaOverlapError(BusinessError):
    def __init__(self):
        msg = "Agenda can not have overlap"
        super().__init__(msg)


class AgendaTooLargeError(BusinessError):
    def __init__(self):
        msg = "Agenda can not end after event end"
        super().__init__(msg)
