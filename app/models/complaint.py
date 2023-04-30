from __future__ import annotations
from enum import Enum
import uuid


class ComplaintType(Enum):
    SPAM = "Spam"
    ILLEGAL = "Contenido ilegal, obsceno, ofensivo o discriminatorio"
    TERMS = "Infringe los términos y condiciones"
    OTHER = "Otros"


class ComplaintOrganizerRanking:
    def __init__(
        self,
        organizer_id: str,
        complaints: int,
    ):
        self.organizer_id = organizer_id
        self.complaints = complaints


class Complaint:
    def __init__(
        self,
        event_id: str,
        complainer_id: str,
        id: str,
        type: ComplaintType,
        description: str,
        organizer_id: str,
    ):
        self.event_id = event_id
        self.complainer_id = complainer_id
        self.id = id
        self.type = type
        self.description = description
        self.organizer_id = organizer_id

    @classmethod
    def new(
        cls,
        event_id: str,
        complainer_id: str,
        type: ComplaintType,
        description: str,
        organizer_id: str,
    ) -> Complaint:
        return Complaint(
            event_id=event_id,
            complainer_id=complainer_id,
            id=str(uuid.uuid4()),
            type=type,
            description=description if description else "",
            organizer_id=organizer_id,
        )
