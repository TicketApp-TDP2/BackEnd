from pydantic import BaseModel, Field


class FavouriteSchema(BaseModel):
    event_id: str = Field(..., min_length=3)
