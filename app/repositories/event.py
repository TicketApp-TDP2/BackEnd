from typing import List, Optional
from app.config.logger import setup_logger
from app.repositories.config import db
from pymongo import GEOSPHERE
from bson.son import SON
from abc import ABC, abstractmethod
from app.models.event import Type, Event, Location
from app.repositories.errors import EventNotFoundError
from datetime import date, time


EARTH_RADIUS_METERS = 6_371_000


class SearchLocation:
    def __init__(self, lat: float, lng: float, dist: int):
        self.lat = lat
        self.lng = lng
        self.dist = dist


class EventRepository(ABC):
    @abstractmethod
    def add_event(self, event: Event) -> Event:
        pass

    @abstractmethod
    def get_event(self, id: str) -> Event:
        pass

    @abstractmethod
    def event_exists(self, id: str) -> bool:
        pass


class PersistentEventRepository(EventRepository):
    def __init__(self):
        COLLECTION_NAME = "Events"
        self.events = db[COLLECTION_NAME]
        self.events.create_index([("location", GEOSPHERE)])

    def add_event(self, event: Event) -> Event:
        data = self.__serialize_event(event)
        self.events.insert_one(data)
        return event

    def get_event(self, id: str) -> Event:
        event = self.events.find_one({'_id': id})
        if event is None:
            raise EventNotFoundError
        return self.__deserialize_event(event)

    def event_exists(self, id: str) -> bool:
        event = self.events.find_one({'_id': id})
        return event is not None

    def __serialize_event(self, event: Event) -> dict:

        serialized = {
            'title': event.title,
            'description': event.description,
            'location': {
                'description': event.location.description,
                'type': 'Point',
                'coordinates': [event.location.lng, event.location.lat],
            },
            'type': event.type.value,
            'images': event.images,
            'preview_image': event.preview_image,
            'date': str(event.date),
            'start_time': str(event.start_time),
            'end_time': str(event.end_time),
            'organizer': event.organizer,
            'agenda': event.agenda,
            'vacants': event.vacants,
            'FAQ': event.FAQ,
            '_id': event.id,
        }

        return serialized

    def __deserialize_event(self, data: dict) -> Event:

        return Event(
            id=data['_id'],
            title=data['title'],
            description=data['description'],
            location=Location(
                description=data['location']['description'],
                lat=data['location']['coordinates'][1],
                lng=data['location']['coordinates'][0],
            ),
            type=Type(data['type']),
            images=data['images'],
            preview_image=data['preview_image'],
            date=date.fromisoformat(data['date']),
            start_time=time.fromisoformat(data['start_time']),
            end_time=time.fromisoformat(data['end_time']),
            organizer=data['organizer'],
            agenda=data['agenda'],
            vacants=data['vacants'],
            FAQ=data['FAQ'],
        )
