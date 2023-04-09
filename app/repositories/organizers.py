from app.repositories.config import db
from abc import ABC, abstractmethod
from app.models.organizer import Organizer
from app.repositories.errors import OrganizerNotFoundError


class OrganizerRepository(ABC):
    @abstractmethod
    def add_organizer(self, organizer: Organizer) -> Organizer:
        pass

    @abstractmethod
    def get_organizer(self, id: str) -> Organizer:
        pass

    @abstractmethod
    def organizer_exists(self, id: str) -> bool:
        pass

    @abstractmethod
    def organizer_exists_by_email(self, email: str) -> bool:
        pass

    @abstractmethod
    def get_organizer_by_email(self, email: str) -> Organizer:
        pass

    @abstractmethod
    def update_organizer(self, organizer: Organizer) -> Organizer:
        pass


class PersistentOrganizerRepository(OrganizerRepository):
    def __init__(self):
        COLLECTION_NAME = "Organizers"
        self.organizers = db[COLLECTION_NAME]

    def add_organizer(self, organizer: Organizer) -> Organizer:
        data = self.__serialize_organizer(organizer)
        self.organizers.insert_one(data)
        return organizer

    def get_organizer(self, id: str) -> Organizer:
        organizer = self.organizers.find_one({'_id': id})
        if organizer is None:
            raise OrganizerNotFoundError
        return self.__deserialize_organizer(organizer)

    def get_organizer_by_email(self, email: str) -> Organizer:
        organizer = self.organizers.find_one({'email': email})
        if organizer is None:
            raise OrganizerNotFoundError
        return self.__deserialize_organizer(organizer)

    def organizer_exists(self, id: str) -> bool:
        organizer = self.organizers.find_one({'_id': id})
        return organizer is not None

    def organizer_exists_by_email(self, email: str) -> bool:
        organizer = self.organizers.find_one({'email': email})
        return organizer is not None

    def update_organizer(self, organizer: Organizer) -> Organizer:
        data = self.__serialize_organizer(organizer)
        self.organizers.update_one({'_id': organizer.id}, {'$set': data})
        return organizer

    def __serialize_organizer(self, organizer: Organizer) -> dict:
        serialized = {
            '_id': organizer.id,
            'first_name': organizer.first_name,
            'last_name': organizer.last_name,
            'email': organizer.email,
            'profession': organizer.profession,
            'about_me': organizer.about_me,
            'profile_picture': organizer.profile_picture,
        }

        return serialized

    def __deserialize_organizer(self, data: dict) -> Organizer:
        return Organizer(
            id=data['_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            profession=data['profession'],
            about_me=data['about_me'],
            profile_picture=data['profile_picture'],
        )
