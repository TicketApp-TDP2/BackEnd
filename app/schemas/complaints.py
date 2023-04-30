from __future__ import annotations
from pydantic import BaseModel, Field
from app.models.complaint import (
    Complaint,
    ComplaintType,
    ComplaintOrganizerRanking,
    ComplaintEventRanking,
)
from typing import Optional


class ComplaintSchemaBase(BaseModel):
    event_id: str = Field(..., min_length=1)
    complainer_id: str = Field(..., min_length=1)
    type: ComplaintType
    description: Optional[str]


class ComplaintCreateSchema(ComplaintSchemaBase):
    pass


class ComplaintOrganizerRankingSchema(BaseModel):
    organizer_id: str = Field(..., min_length=1)
    complaints: int

    @classmethod
    def from_model(
        cls, complaint: ComplaintOrganizerRanking
    ) -> ComplaintOrganizerRankingSchema:
        return ComplaintOrganizerRankingSchema(
            organizer_id=complaint.organizer_id,
            complaints=complaint.complaints,
        )


class ComplaintEventRankingSchema(BaseModel):
    event_id: str = Field(..., min_length=1)
    complaints: int

    @classmethod
    def from_model(
        cls, complaint: ComplaintEventRanking
    ) -> ComplaintEventRankingSchema:
        return ComplaintEventRankingSchema(
            event_id=complaint.event_id,
            complaints=complaint.complaints,
        )


class ComplaintSchema(ComplaintSchemaBase):
    id: str = Field(..., min_length=1)
    organizer_id: str = Field(..., min_length=1)

    @classmethod
    def from_model(cls, complaint: Complaint) -> ComplaintSchema:
        return ComplaintSchema(
            event_id=complaint.event_id,
            complainer_id=complaint.complainer_id,
            id=complaint.id,
            type=ComplaintType(complaint.type),
            description=complaint.description,
            organizer_id=complaint.organizer_id,
        )
