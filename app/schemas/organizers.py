from __future__ import annotations
from pydantic import BaseModel, Field, EmailStr
from app.models.organizer import Organizer

from typing import List, Optional


class OrganizerSchemaBase(BaseModel):
    first_name: str = Field(..., min_length=3)
    last_name: Optional[str]
    email: EmailStr
    profession: Optional[str]
    about_me: Optional[str]
    profile_picture: Optional[str]
    id: str = Field(..., min_length=3)


class OrganizerCreateSchema(OrganizerSchemaBase):
    pass


class OrganizerUpdateSchema(BaseModel):
    first_name: Optional[str] = Field(..., min_length=3)
    last_name: Optional[str] = Field(..., min_length=3)
    profession: Optional[str]
    about_me: Optional[str]
    profile_picture: Optional[str]


class OrganizerSchema(OrganizerSchemaBase):
    suspended: bool

    @classmethod
    def from_model(cls, organizer: Organizer) -> OrganizerSchema:
        return OrganizerSchema(
            first_name=organizer.first_name,
            last_name=organizer.last_name,
            email=EmailStr(organizer.email),
            id=organizer.id,
            profession=organizer.profession if organizer.profession else "",
            about_me=organizer.about_me if organizer.about_me else "",
            profile_picture=organizer.profile_picture
            if organizer.profile_picture
            else "https://i.pinimg.com/736x/83/bc/8b/83bc8b88cf6bc4b4e04d153a418cde62.jpg",
            suspended=organizer.suspended,
        )
