from app.repositories.config import db
from abc import ABC, abstractmethod
from app.models.complaint import Complaint, ComplaintType, ComplaintOrganizerRanking
from app.repositories.errors import ComplaintNotFoundError
from bson.son import SON


class ComplaintRepository(ABC):
    @abstractmethod
    def add_complaint(self, complaint: Complaint) -> Complaint:
        pass

    @abstractmethod
    def get_complaints_by_organizer(self, organizer_id: str) -> list[Complaint]:
        pass

    @abstractmethod
    def get_complaints_by_event(self, event_id: str) -> list[Complaint]:
        pass

    @abstractmethod
    def get_complaint(self, complaint_id: str) -> Complaint:
        pass

    @abstractmethod
    def get_complaints_ranking_by_organizer(self) -> list[ComplaintOrganizerRanking]:
        pass


class PersistentComplaintRepository(ComplaintRepository):
    def __init__(self):
        COLLECTION_NAME = "Complaints"
        self.complaints = db[COLLECTION_NAME]

    def add_complaint(self, complaint: Complaint) -> Complaint:
        data = self.__serialize_complaint(complaint)
        self.complaints.insert_one(data)
        return complaint

    def get_complaints_by_organizer(self, organizer_id: str) -> list[Complaint]:
        complaints = self.complaints.find({'organizer_id': organizer_id})
        return [self.__deserialize_complaint(complaint) for complaint in complaints]

    def get_complaints_by_event(self, event_id: str) -> list[Complaint]:
        complaints = self.complaints.find({'event_id': event_id})
        return [self.__deserialize_complaint(complaint) for complaint in complaints]

    def get_complaint(self, complaint_id: str) -> Complaint:
        complaint = self.complaints.find_one({'_id': complaint_id})
        if complaint is None:
            raise ComplaintNotFoundError
        return self.__deserialize_complaint(complaint)

    def get_complaints_ranking_by_organizer(self) -> list[ComplaintOrganizerRanking]:
        complaints = self.complaints.aggregate(
            [
                {'$group': {'_id': '$organizer_id', 'count': {'$sum': 1}}},
                {'$sort': SON([("count", -1), ("_id", -1)])},
            ]
        )
        print("complaint ", complaints)
        return [
            ComplaintOrganizerRanking(organizer['_id'], organizer['count'])
            for organizer in complaints
        ]

    def __serialize_complaint(self, complaint: Complaint) -> dict:
        serialized = {
            '_id': complaint.id,
            "event_id": complaint.event_id,
            "complainer_id": complaint.complainer_id,
            "type": complaint.type.value,
            "description": complaint.description,
            "organizer_id": complaint.organizer_id,
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
        )
