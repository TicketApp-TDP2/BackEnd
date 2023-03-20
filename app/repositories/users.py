from app.repositories.config import db
from abc import ABC, abstractmethod
from app.models.user import Card, User


class UserRepository(ABC):
    @abstractmethod
    def add_user(self, user: User) -> User:
        pass

    @abstractmethod
    def user_exists_by_email(self, email: str) -> bool:
        pass


class PersistentUserRepository(UserRepository):
    def __init__(self):
        COLLECTION_NAME = "Users"
        self.users = db[COLLECTION_NAME]

    def add_user(self, user: User) -> User:
        data = self.__serialize_user(user)
        self.users.insert_one(data)
        return user

    def user_exists_by_email(self, email: str) -> bool:
        user = self.users.find_one({'email': email})
        return user is not None

    def __serialize_user(self, user: User) -> dict:
        def __serialize_card(card: Card) -> dict:
            return {
                "number": card.number,
                "security_code": card.security_code,
                "expiry_date": card.expiry_date,
            }

        cards = list(map(__serialize_card, user.cards))

        serialized = {
            '_id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'password': user.password,
            'birth_date': user.birth_date,
            'identification_number': user.identification_number,
            'phone_number': user.phone_number,
            'host': user.host,
            'cards': cards,
            'favourites': user.favourites,
        }

        return serialized
