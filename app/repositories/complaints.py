from app.repositories.config import db
from abc import ABC, abstractmethod
from app.models.complaint import (
    Complaint,
    ComplaintType,
    ComplaintOrganizerRanking,
    ComplaintEventRanking,
)
from app.repositories.errors import ComplaintNotFoundError
from bson.son import SON
from datetime import date
from typing import Optional
from app.models.stat import ComplaintsByTimeStat


class Filter:
    def __init__(
        self,
        start: Optional[date],
        end: Optional[date],
    ):
        self.start = start
        self.end = end


class ComplaintRepository(ABC):
    @abstractmethod
    def add_complaint(self, complaint: Complaint) -> Complaint:
        pass

    @abstractmethod
    def get_complaints_by_organizer(
        self, organizer_id: str, filter: Filter
    ) -> list[Complaint]:
        pass

    @abstractmethod
    def get_complaints_by_event(self, event_id: str, filter: Filter) -> list[Complaint]:
        pass

    @abstractmethod
    def get_complaint(self, complaint_id: str) -> Complaint:
        pass

    @abstractmethod
    def complaint_exists(self, event_id: str, complainer_id: str) -> bool:
        pass

    @abstractmethod
    def get_complaints_ranking_by_organizer(
        self, filter: Filter
    ) -> list[ComplaintOrganizerRanking]:
        pass

    @abstractmethod
    def get_complaints_ranking_by_event(
        self, filter: Filter
    ) -> list[ComplaintEventRanking]:
        pass

    @abstractmethod
    def get_complaints_by_time(
        self, start: str, end: str
    ) -> list[ComplaintsByTimeStat]:
        pass


class PersistentComplaintRepository(ComplaintRepository):
    def __init__(self):
        COLLECTION_NAME = "Complaints"
        self.complaints = db[COLLECTION_NAME]

    def add_complaint(self, complaint: Complaint) -> Complaint:
        data = self.__serialize_complaint(complaint)
        self.complaints.insert_one(data)
        return complaint

    def complaint_exists(self, event_id: str, complainer_id: str) -> bool:
        complaint = self.complaints.find_one(
            {'event_id': event_id, "complainer_id": complainer_id}
        )
        return complaint is not None

    def get_complaints_by_organizer(
        self, organizer_id: str, filter: Filter
    ) -> list[Complaint]:
        pipeline = self.__get_pipeline(filter)
        pipeline.append({'$match': {'organizer_id': organizer_id}})
        complaints = self.complaints.aggregate(pipeline)
        return [self.__deserialize_complaint(complaint) for complaint in complaints]

    def get_complaints_by_event(self, event_id: str, filter: Filter) -> list[Complaint]:
        pipeline = self.__get_pipeline(filter)
        pipeline.append({'$match': {'event_id': event_id}})
        complaints = self.complaints.aggregate(pipeline)
        return [self.__deserialize_complaint(complaint) for complaint in complaints]

    def get_complaint(self, complaint_id: str) -> Complaint:
        complaint = self.complaints.find_one({'_id': complaint_id})
        if complaint is None:
            raise ComplaintNotFoundError
        return self.__deserialize_complaint(complaint)

    def get_complaints_ranking_by_organizer(
        self, filter: Filter
    ) -> list[ComplaintOrganizerRanking]:
        pipeline = self.__get_pipeline(filter)
        pipeline.append({'$group': {'_id': '$organizer_id', 'count': {'$sum': 1}}})
        pipeline.append({'$sort': SON([("count", -1), ("_id", -1)])})

        ranking = self.complaints.aggregate(pipeline)
        return [
            ComplaintOrganizerRanking(organizer['_id'], organizer['count'])
            for organizer in ranking
        ]

    def get_complaints_ranking_by_event(
        self, filter: Filter
    ) -> list[ComplaintEventRanking]:
        pipeline = self.__get_pipeline(filter)
        pipeline.append({'$group': {'_id': '$event_id', 'count': {'$sum': 1}}})
        pipeline.append({'$sort': SON([("count", -1), ("_id", -1)])})
        ranking = self.complaints.aggregate(pipeline)
        return [
            ComplaintEventRanking(event['_id'], event['count']) for event in ranking
        ]

    def get_complaints_by_time(
        self, start: str, end: str
    ) -> list[ComplaintsByTimeStat]:
        pipeline = [
            {'$match': {'date': {'$gte': start, '$lte': end}}},
            {'$project': {'date': {'$substr': ['$date', 0, 7]}}},
            {'$group': {'_id': '$date', 'count': {'$sum': 1}}},
            {'$sort': {'_id': 1}},
        ]
        stats = self.complaints.aggregate(pipeline)
        return [ComplaintsByTimeStat(stat['_id'], stat['count']) for stat in stats]

    def __get_pipeline(self, filter: Filter):
        pipeline = []
        if filter.start:
            pipeline.append({'$match': {'date': {'$gte': filter.start.isoformat()}}})
        if filter.end:
            pipeline.append({'$match': {'date': {'$lte': filter.end.isoformat()}}})
        return pipeline

    def __serialize_complaint(self, complaint: Complaint) -> dict:
        serialized = {
            '_id': complaint.id,
            "event_id": complaint.event_id,
            "complainer_id": complaint.complainer_id,
            "type": complaint.type.value,
            "description": complaint.description,
            "organizer_id": complaint.organizer_id,
            "date": str(complaint.date),
        }

        return serialized

    def __deserialize_complaint(self, data: dict) -> Complaint:
        return Complaint(
            id=data['_id'],
            event_id=data['event_id'],
            complainer_id=data['complainer_id'],
            type=ComplaintType(data['type']),
            description=data['description'],
            organizer_id=data['organizer_id'],
            date=date.fromisoformat(data['date']),
        )
