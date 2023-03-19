from __future__ import annotations
from pydantic import BaseModel, Field, EmailStr
from app.models.user import User, Card
from typing import List


class CardSchemaBase(BaseModel):
    number: str = Field(..., min_length=3)
    security_code: str = Field(..., min_length=3)
    expiry_date: str = Field(..., min_length=3)


class CardCreateSchema(CardSchemaBase):
    pass


class CardSchema(CardSchemaBase):
    @classmethod
    def from_model(cls, card: Card) -> CardSchema:
        return CardSchema(
            number=card.number,
            security_code=card.security_code,
            expiry_date=card.expiry_date,
        )


class UserSchemaBase(BaseModel):
    first_name: str = Field(..., min_length=3)
    last_name: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=3)
    birth_date: str = Field(..., min_length=3)
    identification_number: str
    phone_number: str
    host: bool


class UserCreateSchema(UserSchemaBase):
    pass


class UserSchema(UserSchemaBase):
    id: str = Field(..., min_length=1)
    cards: List[CardSchema] = Field(...)

    @classmethod
    def from_model(cls, user: User) -> UserSchema:

        cards = list(map(lambda x: CardSchema.from_model(x), user.cards))

        return UserSchema(
            first_name=user.first_name,
            last_name=user.last_name,
            email=EmailStr(user.email),
            id=user.id if user.id else "",
            password=user.password,
            birth_date=user.birth_date,
            identification_number=user.identification_number,
            phone_number=user.phone_number,
            host=user.host,
            cards=cards,
        )
