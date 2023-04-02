from __future__ import annotations
from pydantic import BaseModel, Field, EmailStr
from app.models.organizer import Organizer
from typing import List


class OrganizerSchemaBase(BaseModel):
    first_name: str = Field(..., min_length=3)
    last_name: str = Field(..., min_length=3)
    email: EmailStr
    profession: str = Field(..., min_length=3)
    about_me: str = Field(..., min_length=3)
    profile_picture: str = Field(..., min_length=3)
    id: str = Field(..., min_length=1)


class OrganizerCreateSchema(OrganizerSchemaBase):
    pass


class OrganizerSchema(OrganizerSchemaBase):
    @classmethod
    def from_model(cls, organizer: Organizer) -> OrganizerSchema:

        return OrganizerSchema(
            first_name=organizer.first_name,
            last_name=organizer.last_name,
            email=EmailStr(organizer.email),
            id=organizer.id if organizer.id else "",
            profession=organizer.profession,
            about_me=organizer.about_me,
            profile_picture=organizer.profile_picture,
        )
