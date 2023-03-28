from __future__ import annotations
from pydantic import BaseModel, Field, EmailStr
from app.models.user import User
from typing import List


class UserSchemaBase(BaseModel):
    first_name: str = Field(..., min_length=3)
    last_name: str = Field(..., min_length=3)
    email: EmailStr
    birth_date: str = Field(..., min_length=3)
    identification_number: str
    phone_number: str


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
            id=user.id if user.id else "",
            birth_date=user.birth_date,
            identification_number=user.identification_number,
            phone_number=user.phone_number,
        )
