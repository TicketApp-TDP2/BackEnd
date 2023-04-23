from __future__ import annotations
from pydantic import BaseModel, Field, EmailStr
from app.models.user import User
from typing import List, Optional


class UserSchemaBase(BaseModel):
    first_name: str = Field(..., min_length=3)
    last_name: Optional[str]
    email: EmailStr
    birth_date: Optional[str]
    identification_number: Optional[str]
    phone_number: Optional[str]
    id: str = Field(..., min_length=3)


class UserCreateSchema(UserSchemaBase):
    pass


class UserSchema(UserSchemaBase):
    id: str = Field(..., min_length=1)

    @classmethod
    def from_model(cls, user: User) -> UserSchema:
        return UserSchema(
            first_name=user.first_name,
            last_name=user.last_name,
            email=EmailStr(user.email),
            id=user.id,
            birth_date=user.birth_date if user.birth_date else "1900-01-01",
            identification_number=user.identification_number
            if user.identification_number
            else "",
            phone_number=user.phone_number if user.phone_number else "",
        )
