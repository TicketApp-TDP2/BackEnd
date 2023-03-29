from app.models.errors import BusinessError


class OrganizerNotFoundError(BusinessError):
    def __init__(self):
        msg = "Organizer not found"
        super().__init__(msg)


class OrganizerAlreadyExistsError(BusinessError):
    def __init__(self):
        msg = "Organizer already exists"
        super().__init__(msg)
