from app.models.errors import BusinessError


class UserNotFoundError(BusinessError):
    def __init__(self):
        msg = "User not found"
        super().__init__(msg)


class UserAlreadyExistsError(BusinessError):
    def __init__(self):
        msg = "User already exists"
        super().__init__(msg)
