from app.repositories.config import db
from abc import ABC, abstractmethod
from app.models.user import Card, User
from app.repositories.errors import UserNotFoundError


class UserRepository(ABC):
    @abstractmethod
    def add_user(self, user: User) -> User:
        pass

    @abstractmethod
    def get_user(self, id: str) -> User:
        pass

    @abstractmethod
    def user_exists(self, id: str) -> bool:
        pass

    @abstractmethod
    def user_exists_by_email(self, email: str) -> bool:
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> User:
        pass

    @abstractmethod
    def update_user(self, user: User) -> User:
        pass


class PersistentUserRepository(UserRepository):
    def __init__(self):
        COLLECTION_NAME = "Users"
        self.users = db[COLLECTION_NAME]

    def add_user(self, user: User) -> User:
        data = self.__serialize_user(user)
        self.users.insert_one(data)
        return user

    def get_user(self, id: str) -> User:
        user = self.users.find_one({'_id': id})
        if user is None:
            raise UserNotFoundError
        return self.__deserialize_user(user)

    def get_user_by_email(self, email: str) -> User:
        user = self.users.find_one({'email': email})
        if user is None:
            raise UserNotFoundError
        return self.__deserialize_user(user)

    def user_exists(self, id: str) -> bool:
        user = self.users.find_one({'_id': id})
        return user is not None

    def user_exists_by_email(self, email: str) -> bool:
        user = self.users.find_one({'email': email})
        return user is not None

    def update_user(self, user: User) -> User:
        data = self.__serialize_user(user)
        self.users.update_one({'_id': user.id}, {'$set': data})
        return user

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

    def __deserialize_user(self, data: dict) -> User:
        def __deserialize_card(card: dict) -> Card:
            return Card(
                number=card['number'],
                security_code=card['security_code'],
                expiry_date=card['expiry_date'],
            )

        def __deserialize_favourite(card: dict) -> Card:
            return Card(
                number=card['number'],
                security_code=card['security_code'],
                expiry_date=card['expiry_date'],
            )

        cards = list(map(__deserialize_card, data['cards']))

        cards = list(map(__deserialize_card, data['cards']))

        return User(
            id=data['_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            password=data['password'],
            birth_date=data['birth_date'],
            identification_number=data['identification_number'],
            phone_number=data['phone_number'],
            host=data['host'],
            cards=cards,
            favourites=data['favourites'],
        )
