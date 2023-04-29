from __future__ import annotations
from pydantic import BaseModel, Field
from app.models.complaint import Complaint, ComplaintType
from typing import Optional


class ComplaintSchemaBase(BaseModel):
    event_id: str = Field(..., min_length=1)
    complainer_id: str = Field(..., min_length=1)
    type: ComplaintType
    description: Optional[str]
    organizer_id: str = Field(..., min_length=1)


class ComplaintCreateSchema(ComplaintSchemaBase):
    pass


class ComplaintSchema(ComplaintSchemaBase):
    id: str = Field(..., min_length=1)

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
