from app.schemas.complaints import (
    ComplaintCreateSchema,
    ComplaintSchema,
    ComplaintOrganizerRankingSchema,
    ComplaintEventRankingSchema,
)
from app.models.complaint import Complaint
from app.repositories.complaints import ComplaintRepository, Filter
from app.repositories.event import EventRepository
from app.config.logger import setup_logger
from typing import List
from app.commands.complaints.errors import ComplaintAlreadyExistsError

logger = setup_logger(__name__)


class CreateComplaintCommand:
    def __init__(
        self,
        complaint_repository: ComplaintRepository,
        event_repository: EventRepository,
        complaint: ComplaintCreateSchema,
    ):
        self.complaint_repository = complaint_repository
        self.complaint_data = complaint
        self.event_repository = event_repository

    def execute(self) -> ComplaintSchema:
        event = self.event_repository.get_event(self.complaint_data.event_id)
        organizer_id = event.organizer
        if self.complaint_repository.complaint_exists(
            self.complaint_data.event_id, self.complaint_data.complainer_id
        ):
            raise ComplaintAlreadyExistsError

        complaint = Complaint.new(
            event_id=self.complaint_data.event_id,
            complainer_id=self.complaint_data.complainer_id,
            type=self.complaint_data.type,
            description=self.complaint_data.description,
            organizer_id=organizer_id,
        )

        complaint = self.complaint_repository.add_complaint(complaint)

        return ComplaintSchema.from_model(complaint)


class GetComplaintsByOrganizerCommand:
    def __init__(
        self,
        complaint_repository: ComplaintRepository,
        organizer_id: str,
        filter: Filter,
    ):
        self.complaint_repository = complaint_repository
        self.organizer_id = organizer_id
        self.filter = filter

    def execute(self) -> List[ComplaintSchema]:
        complaints = self.complaint_repository.get_complaints_by_organizer(
            self.organizer_id, self.filter
        )
        return [ComplaintSchema.from_model(complaint) for complaint in complaints]


class GetComplaintsByEventCommand:
    def __init__(
        self, complaint_repository: ComplaintRepository, event_id: str, filter: Filter
    ):
        self.complaint_repository = complaint_repository
        self.event_id = event_id
        self.filter = filter

    def execute(self) -> List[ComplaintSchema]:
        complaints = self.complaint_repository.get_complaints_by_event(
            self.event_id, self.filter
        )
        return [ComplaintSchema.from_model(complaint) for complaint in complaints]


class GetComplaintCommand:
    def __init__(self, complaint_repository: ComplaintRepository, complaint_id: str):
        self.complaint_repository = complaint_repository
        self.complaint_id = complaint_id

    def execute(self) -> List[ComplaintSchema]:
        complaint = self.complaint_repository.get_complaint(self.complaint_id)
        return ComplaintSchema.from_model(complaint)


class GetComplaintsRankingByOrganizerCommand:
    def __init__(self, complaint_repository: ComplaintRepository, filter: Filter):
        self.complaint_repository = complaint_repository
        self.filter = filter

    def execute(self) -> List[ComplaintOrganizerRankingSchema]:
        ranking = self.complaint_repository.get_complaints_ranking_by_organizer(
            self.filter
        )
        return [ComplaintOrganizerRankingSchema.from_model(rank) for rank in ranking]


class GetComplaintsRankingByEventCommand:
    def __init__(self, complaint_repository: ComplaintRepository, filter: Filter):
        self.complaint_repository = complaint_repository
        self.filter = filter

    def execute(self) -> List[ComplaintEventRankingSchema]:
        ranking = self.complaint_repository.get_complaints_ranking_by_event(self.filter)
        return [ComplaintEventRankingSchema.from_model(rank) for rank in ranking]
