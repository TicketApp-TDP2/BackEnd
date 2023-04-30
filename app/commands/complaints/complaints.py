from app.schemas.complaints import ComplaintCreateSchema, ComplaintSchema
from app.models.complaint import Complaint
from app.repositories.complaints import (
    ComplaintRepository,
)
from app.config.logger import setup_logger
from typing import List

logger = setup_logger(__name__)


class CreateComplaintCommand:
    def __init__(
        self,
        complaint_repository: ComplaintRepository,
        complaint: ComplaintCreateSchema,
    ):
        self.complaint_repository = complaint_repository
        self.complaint_data = complaint

    def execute(self) -> ComplaintSchema:
        complaint = Complaint.new(
            event_id=self.complaint_data.event_id,
            complainer_id=self.complaint_data.complainer_id,
            type=self.complaint_data.type,
            description=self.complaint_data.description,
            organizer_id=self.complaint_data.organizer_id,
        )

        complaint = self.complaint_repository.add_complaint(complaint)

        return ComplaintSchema.from_model(complaint)


class GetComplaintsByOrganizerCommand:
    def __init__(self, complaint_repository: ComplaintRepository, organizer_id: str):
        self.complaint_repository = complaint_repository
        self.organizer_id = organizer_id

    def execute(self) -> List[ComplaintSchema]:
        complaints = self.complaint_repository.get_complaints_by_organizer(
            self.organizer_id
        )
        return [ComplaintSchema.from_model(complaint) for complaint in complaints]


class GetComplaintCommand:
    def __init__(self, complaint_repository: ComplaintRepository, complaint_id: str):
        self.complaint_repository = complaint_repository
        self.complaint_id = complaint_id

    def execute(self) -> List[ComplaintSchema]:
        complaint = self.complaint_repository.get_complaint(self.complaint_id)
        return ComplaintSchema.from_model(complaint)
