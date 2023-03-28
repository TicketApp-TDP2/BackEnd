from app.repositories.config import db
from abc import ABC, abstractmethod
from app.models.user import User
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
        serialized = {
            '_id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'birth_date': user.birth_date,
            'identification_number': user.identification_number,
            'phone_number': user.phone_number,
        }

        return serialized

    def __deserialize_user(self, data: dict) -> User:
        return User(
            id=data['_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            birth_date=data['birth_date'],
            identification_number=data['identification_number'],
            phone_number=data['phone_number'],
        )
