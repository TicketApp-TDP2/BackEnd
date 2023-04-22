from app.models.errors import BusinessError


class UserNotFoundError(BusinessError):
    def __init__(self):
        msg = "user_not_found"
        super().__init__(msg)


class UserAlreadyExistsError(BusinessError):
    def __init__(self):
        msg = "user_already_exists"
        super().__init__(msg)
