from abc import ABC, abstractmethod
from typing import List
from app.models.image import Image
from app.config.constants import IMAGES_PATH
from pathlib import Path

from app.repositories.errors import ImageNotFoundError


class ImageRepository(ABC):
    @abstractmethod
    def add_images(self, images: List[Image]) -> List[Image]:
        pass

    @abstractmethod
    def get_image(self) -> Image:
        pass


class PersistentImageRepository(ImageRepository):
    def __init__(self):
        self.images_path = Path(IMAGES_PATH)
        self.images_path.mkdir(parents=True, exist_ok=True)

    def add_images(self, images: List[Image]) -> List[Image]:
        for img in images:
            with open(self.images_path / img.name, "wb") as fd:
                fd.write(img.content)

        return images

    def get_image(self, name: str) -> Image:
        try:
            with open(self.images_path / name, 'rb') as fd:
                content = fd.read()
                return Image(name=name, content=content)
        except Exception:
            raise ImageNotFoundError()
