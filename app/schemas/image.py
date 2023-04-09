from __future__ import annotations
from pydantic import BaseModel
from app.models.image import Image


class ImageSchema(BaseModel):
    name: str

    @classmethod
    def from_model(cls, image: Image) -> ImageSchema:
        return ImageSchema(
            name=image.name,
        )
