from app.models.errors import BusinessError


class OrganizerNotFoundError(BusinessError):
    def __init__(self):
        msg = "organizer_not_found"
        super().__init__(msg)


class OrganizerAlreadyExistsError(BusinessError):
    def __init__(self):
        msg = "organizer_already_exists"
        super().__init__(msg)
