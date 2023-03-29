from __future__ import annotations
from pydantic import BaseModel, Field, EmailStr
from app.models.organizer import Organizer
from typing import List


class OrganizerSchemaBase(BaseModel):
    first_name: str = Field(..., min_length=3)
    last_name: str = Field(..., min_length=3)
    email: EmailStr
    birth_date: str = Field(..., min_length=3)
    identification_number: str
    phone_number: str


class OrganizerCreateSchema(OrganizerSchemaBase):
    pass


class OrganizerSchema(OrganizerSchemaBase):
    id: str = Field(..., min_length=1)

    @classmethod
    def from_model(cls, organizer: Organizer) -> OrganizerSchema:

        return OrganizerSchema(
            first_name=organizer.first_name,
            last_name=organizer.last_name,
            email=EmailStr(organizer.email),
            id=organizer.id if organizer.id else "",
            birth_date=organizer.birth_date,
            identification_number=organizer.identification_number,
            phone_number=organizer.phone_number,
        )
