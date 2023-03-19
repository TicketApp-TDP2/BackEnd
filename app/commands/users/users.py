from app.schemas.users import UserCreateSchema, UserSchema, CardCreateSchema
from app.models.user import User, Card
from .errors import UserAlreadyExistsError, UserNotFoundError
from app.repositories import (
    UserRepository,
)
from app.config.logger import setup_logger
import uuid

logger = setup_logger(__name__)


class CreateUserCommand:
    def __init__(self, user_repository: UserRepository, user: UserCreateSchema):
        self.user_repository = user_repository
        self.user_data = user

    def execute(self) -> UserSchema:
        user = User(
            first_name=self.user_data.first_name,
            last_name=self.user_data.last_name,
            email=self.user_data.email,
            password=self.user_data.password,
            birth_date=self.user_data.birth_date,
            host=self.user_data.host,
            identification_number=self.user_data.identification_number,
            phone_number=self.user_data.phone_number,
            cards=[],
            favourites=[],
            id=str(uuid.uuid4()),
        )
        already_exists = self.user_repository.user_exists_by_email(user.email)
        if already_exists:
            raise UserAlreadyExistsError
        user = self.user_repository.add_user(user)

        return UserSchema.from_model(user)


class GetUserCommand:
    def __init__(self, user_repository: UserRepository, _id: str):
        self.user_repository = user_repository
        self.id = _id

    def execute(self) -> UserSchema:

        exists = self.user_repository.user_exists(self.id)
        if not exists:
            raise UserNotFoundError
        user = self.user_repository.get_user(self.id)

        return UserSchema.from_model(user)


class UpdateUserCommand:
    def __init__(
        self, user_repository: UserRepository, card: CardCreateSchema, id: str
    ):
        self.user_repository = user_repository
        self.card_data = card
        self.id = id

    def execute(self) -> UserSchema:
        user = self.user_repository.get_user(self.id)
        cards = user.cards
        cards.append(
            Card(
                number=self.card_data.number,
                expiry_date=self.card_data.expiry_date,
                security_code=self.card_data.security_code,
            )
        )
        user = User(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            password=user.password,
            birth_date=user.birth_date,
            identification_number=user.identification_number,
            phone_number=user.phone_number,
            host=user.host,
            cards=cards,
            favourites=user.favourites,
            id=user.id,
        )
        user = self.user_repository.update_user(user)

        return UserSchema.from_model(user)
