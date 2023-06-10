from typing import List, Optional
from app.config.logger import setup_logger
from app.repositories.config import db
from pymongo import GEOSPHERE
from bson.son import SON
from abc import ABC, abstractmethod
from app.models.event import Type, Event, Location, Agenda, Faq, State, Collaborator
from app.repositories.errors import EventNotFoundError
from datetime import date, time, timedelta
from app.utils.now import getNow
from app.models.stat import (
    EventStatesStat,
    OrganizerStat,
    SuspendedEventStat,
    EventByTimeStat,
    EventPublishedByTimeStat,
)

EARTH_RADIUS_METERS = 6_371_000


class SearchLocation:
    def __init__(self, lat: float, lng: float, dist: int):
        self.lat = lat
        self.lng = lng
        self.dist = dist


class Search:
    def __init__(
        self,
        organizer: Optional[str],
        type: Optional[Type],
        location: Optional[SearchLocation],
        limit: int,
        name: str,
        only_published: bool,
        not_finished: bool,
    ):
        self.organizer = organizer
        self.type = type
        self.location = location
        self.limit = limit
        self.name = name
        self.only_published = only_published
        self.not_finished = not_finished


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

    @abstractmethod
    def search_events(self, search: Search) -> List[Event]:
        pass

    @abstractmethod
    def get_events_by_id(self, ids: List[str]) -> List[Event]:
        pass

    @abstractmethod
    def get_events_by_id_with_date_filter(self, ids: List[str]) -> List[Event]:
        pass

    @abstractmethod
    def update_vacants_left_event(self, id: str, vacants_left: int) -> Event:
        pass

    @abstractmethod
    def update_state_event(self, id: str, state: State) -> Event:
        pass

    @abstractmethod
    def update_published_at(self, id: str, published_at: str) -> Event:
        pass

    @abstractmethod
    def update_verified_vacants(self, id: str, verified_vacants: int) -> Event:
        pass

    @abstractmethod
    def update_event(self, id: str, event: Event) -> Event:
        pass

    @abstractmethod
    def get_event_states_stat(self, start_date: str, end_date: str) -> EventStatesStat:
        pass

    @abstractmethod
    def get_suspended_by_time(self, start: str, end: str) -> list[SuspendedEventStat]:
        pass

    @abstractmethod
    def update_state_all_events(self):
        pass

    @abstractmethod
    def get_top_organizers_stat(
        self, start_date: str, end_date: str
    ) -> list[OrganizerStat]:
        pass

    @abstractmethod
    def update_suspended_at(self, id: str, suspended_at: str) -> Event:
        pass

    @abstractmethod
    def get_events_by_time(
        self, start_date: str, end_date: str
    ) -> list[EventByTimeStat]:
        pass

    @abstractmethod
    def get_events_published_by_time(
        self, start_date: str, end_date: str
    ) -> list[EventPublishedByTimeStat]:
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

    def search_events(self, search: Search) -> List[Event]:
        serialized_search = self.__serialize_search(search)
        events = self.events.find(serialized_search).limit(search.limit)
        return list(map(self.__deserialize_event, events))

    def get_events_by_id(self, ids: List[str]) -> List[Event]:
        events = self.events.find({'_id': {'$in': ids}})
        return list(map(self.__deserialize_event, events))

    def get_events_by_id_with_date_filter(self, ids: List[str]) -> List[Event]:
        now = getNow()
        four_days_ago = now - timedelta(days=4)
        pipeline = {
            '_id': {'$in': ids},
            '$or': [
                {'date': {'$gt': four_days_ago.date().isoformat()}},
                {
                    '$and': [
                        {'date': {'$eq': four_days_ago.date().isoformat()}},
                        {'end_time': {'$gt': four_days_ago.time().isoformat()}},
                    ]
                },
            ],
        }
        events = self.events.find(pipeline)
        return list(map(self.__deserialize_event, events))

    def update_vacants_left_event(self, id: str, vacants_left: int) -> Event:
        event = self.get_event(id)
        event.vacants_left = vacants_left
        data = self.__serialize_event(event)
        self.events.update_one({'_id': id}, {'$set': data})
        return event

    def update_state_event(self, id: str, state: State) -> Event:
        event = self.get_event(id)
        event.state = state
        data = self.__serialize_event(event)
        self.events.update_one({'_id': id}, {'$set': data})
        return event

    def update_verified_vacants(self, id: str, verified_vacants: int) -> Event:
        event = self.get_event(id)
        event.verified_vacants = verified_vacants
        data = self.__serialize_event(event)
        self.events.update_one({'_id': id}, {'$set': data})
        return event

    def update_event(self, event: Event) -> Event:
        data = self.__serialize_event(event)
        self.events.update_one({'_id': event.id}, {'$set': data})
        return event

    def update_suspended_at(self, id: str, suspended_at: str) -> Event:
        event = self.get_event(id)
        event.suspended_at = suspended_at
        data = self.__serialize_event(event)
        self.events.update_one({'_id': id}, {'$set': data})
        return event

    def update_published_at(self, id: str, published_at: str) -> Event:
        event = self.get_event(id)
        event.published_at = published_at
        data = self.__serialize_event(event)
        self.events.update_one({'_id': id}, {'$set': data})
        return event

    def get_event_states_stat(self, start_date: str, end_date: str) -> EventStatesStat:
        pipeline = [
            {
                '$match': {
                    'created_at': {
                        '$gte': start_date,
                        '$lte': end_date,
                    }
                }
            },
            {
                '$group': {
                    '_id': '$state',
                    'count': {'$sum': 1},
                }
            },
            {
                '$project': {
                    'state': '$_id',
                    'count': '$count',
                }
            },
        ]
        result = self.events.aggregate(pipeline)
        result = {doc['state']: doc['count'] for doc in result}
        return EventStatesStat(
            Borrador=result.get(State.Borrador.value, 0),
            Publicado=result.get(State.Publicado.value, 0),
            Cancelado=result.get(State.Cancelado.value, 0),
            Finalizado=result.get(State.Finalizado.value, 0),
            Suspendido=result.get(State.Suspendido.value, 0),
        )

    def update_state_all_events(self):
        now = getNow()
        filter_pipeline = {
            '$or': [
                {'date': {'$lt': now.date().isoformat()}},
                {
                    '$and': [
                        {'date': {'$eq': now.date().isoformat()}},
                        {'end_time': {'$lt': now.time().isoformat()}},
                    ]
                },
            ]
        }

        update_pipeline = {
            '$set': {
                'state': State.Finalizado.value,
            }
        }

        self.events.update_many(filter=filter_pipeline, update=update_pipeline)

    def get_top_organizers_stat(
        self, start_date: str, end_date: str
    ) -> list[OrganizerStat]:
        pipeline = [
            {
                '$match': {
                    'created_at': {
                        '$gte': start_date,
                        '$lte': end_date,
                    }
                }
            },
            {
                '$group': {
                    '_id': '$organizer',
                    'count': {'$sum': '$verified_vacants'},
                }
            },
            {
                '$project': {
                    'organizer': '$_id',
                    'count': '$count',
                }
            },
            {'$match': {'count': {'$gt': 0}}},
            {'$sort': {'count': -1}},
            {'$limit': 10},
        ]
        result = self.events.aggregate(pipeline)
        return [
            OrganizerStat(
                name=doc['organizer'],
                verified_bookings=doc['count'],
                id=doc['organizer'],
            )
            for doc in result
        ]

    def get_events_by_time(
        self, start_date: str, end_date: str
    ) -> list[EventByTimeStat]:
        pipeline = [
            {
                '$match': {
                    'created_at': {
                        '$gte': start_date,
                        '$lte': end_date,
                    }
                }
            },
            {'$project': {'created_at': {'$substr': ['$created_at', 0, 7]}}},
            {
                '$group': {
                    '_id': '$created_at',
                    'count': {'$sum': 1},
                }
            },
            {
                '$project': {
                    'created_at': '$_id',
                    'count': '$count',
                }
            },
            {'$sort': {'created_at': 1}},
        ]
        result = self.events.aggregate(pipeline)
        return [
            EventByTimeStat(
                date=doc['created_at'],
                events=doc['count'],
            )
            for doc in result
        ]

    def get_events_published_by_time(
        self, start_date: str, end_date: str
    ) -> list[EventPublishedByTimeStat]:
        pipeline = [
            {
                '$match': {
                    'published_at': {
                        '$ne': "Not_published",
                    }
                }
            },
            {
                '$match': {
                    'published_at': {
                        '$gte': start_date,
                        '$lte': end_date,
                    }
                }
            },
            {'$project': {'published_at': {'$substr': ['$published_at', 0, 7]}}},
            {
                '$group': {
                    '_id': '$published_at',
                    'count': {'$sum': 1},
                }
            },
            {
                '$project': {
                    'published_at': '$_id',
                    'count': '$count',
                }
            },
            {'$sort': {'published_at': 1}},
        ]
        result = self.events.aggregate(pipeline)
        return [
            EventByTimeStat(
                date=doc['published_at'],
                events=doc['count'],
            )
            for doc in result
        ]

    def get_suspended_by_time(self, start: str, end: str) -> list[SuspendedEventStat]:
        pipeline = [
            {
                '$match': {
                    'suspended_at': {
                        '$ne': "Not_suspended",
                    }
                }
            },
            {
                '$match': {
                    'suspended_at': {
                        '$gte': start,
                        '$lte': end,
                    }
                }
            },
            {'$project': {'suspended_at': {'$substr': ['$suspended_at', 0, 7]}}},
            {
                '$group': {
                    '_id': '$suspended_at',
                    'count': {'$sum': 1},
                }
            },
            {
                '$project': {
                    'suspended_at': '$_id',
                    'count': '$count',
                }
            },
            {'$sort': {'suspended_at': 1}},
        ]
        result = self.events.aggregate(pipeline)
        return [
            SuspendedEventStat(
                date=doc['suspended_at'],
                suspended=doc['count'],
            )
            for doc in result
        ]

    def __serialize_search(self, search: Search) -> dict:
        srch = {
            'type': search.type and search.type.value,
        }

        if search.organizer:
            now = getNow()
            four_days_ago = now - timedelta(days=4)
            srch["$and"] = [
                {
                    "$or": [
                        {'organizer': search.organizer},
                        {'collaborators': {'$elemMatch': {'id': search.organizer}}},
                    ]
                },
                {
                    '$or': [
                        {'date': {'$gt': four_days_ago.date().isoformat()}},
                        {
                            '$and': [
                                {'date': {'$eq': four_days_ago.date().isoformat()}},
                                {'end_time': {'$gt': four_days_ago.time().isoformat()}},
                            ]
                        },
                    ]
                },
            ]

        if search.name:
            srch['name'] = {'$regex': search.name, '$options': 'i'}

        if search.only_published:
            srch['state'] = State.Publicado.value

        if search.not_finished:
            now = getNow()
            srch['$or'] = [
                {
                    '$and': [
                        {'date': {'$gt': now.date().isoformat()}},
                    ]
                },
                {
                    '$and': [
                        {'date': {'$eq': now.date().isoformat()}},
                        {'end_time': {'$gt': now.time().isoformat()}},
                    ]
                },
            ]

        if search.location:
            lng = search.location.lng
            lat = search.location.lat
            dist = search.location.dist
            srch['location'] = SON(
                [
                    ("$nearSphere", [lng, lat]),
                    ("$maxDistance", dist / EARTH_RADIUS_METERS),
                ]
            )

        return {k: v for k, v in srch.items() if v is not None}

    def __serialize_agenda(self, agenda):
        serialized_agenda = [
            {
                'time_init': element.time_init,
                'time_end': element.time_end,
                'title': element.title,
                'owner': element.owner,
                'description': element.description,
            }
            for element in agenda
        ]
        return serialized_agenda

    def __serialize_faq(self, faq):
        serialized_faq = [
            {
                'question': element.question,
                'answer': element.answer,
            }
            for element in faq
        ]
        return serialized_faq

    def __serialize_collaborators(self, collaborators):
        serialized_collaborators = [
            {
                'id': element.id,
                'email': element.email,
            }
            for element in collaborators
        ]
        return serialized_collaborators

    def __serialize_event(self, event: Event) -> dict:
        serialized_agenda = self.__serialize_agenda(event.agenda)
        serialized_faq = self.__serialize_faq(event.FAQ)
        serialized_collaborators = self.__serialize_collaborators(event.collaborators)

        serialized = {
            'name': event.name,
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
            'scan_time': event.scan_time,
            'organizer': event.organizer,
            'agenda': serialized_agenda,
            'vacants': event.vacants,
            'vacants_left': event.vacants_left,
            'FAQ': serialized_faq,
            '_id': event.id,
            'state': event.state.value,
            'verified_vacants': event.verified_vacants,
            'collaborators': serialized_collaborators,
            'created_at': str(event.created_at),
            'suspended_at': event.suspended_at,
            'published_at': event.published_at,
        }

        return serialized

    def __deserialize_agenda(self, agenda):
        deserialized_agenda = [
            Agenda(
                time_init=element['time_init'],
                time_end=element['time_end'],
                title=element['title'],
                owner=element['owner'],
                description=element['description'],
            )
            for element in agenda
        ]
        return deserialized_agenda

    def __deserialize_faq(self, faq):
        deserialized_faq = [
            Faq(
                question=element['question'],
                answer=element['answer'],
            )
            for element in faq
        ]
        return deserialized_faq

    def __deserialize_collaborators(self, collaborators):
        deserialized_collaborators = [
            Collaborator(
                id=element['id'],
                email=element['email'],
            )
            for element in collaborators
        ]
        return deserialized_collaborators

    def __deserialize_event(self, data: dict) -> Event:
        deserialized_agenda = self.__deserialize_agenda(data['agenda'])
        deserialized_faq = self.__deserialize_faq(data['FAQ'])
        deserialized_collaborators = self.__deserialize_collaborators(
            data['collaborators']
        )

        return Event(
            id=data['_id'],
            name=data['name'],
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
            scan_time=data['scan_time'],
            organizer=data['organizer'],
            agenda=deserialized_agenda,
            vacants=data['vacants'],
            vacants_left=data['vacants_left'],
            FAQ=deserialized_faq,
            state=State(data['state']),
            verified_vacants=data['verified_vacants'],
            collaborators=deserialized_collaborators,
            created_at=date.fromisoformat(data['created_at']),
            suspended_at=data['suspended_at'],
            published_at=data['published_at'],
        )
