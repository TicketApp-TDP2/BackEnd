from typing import List
from fastapi import UploadFile
import uuid
from app.config.constants import MAX_IMAGE_SIZE, MAX_IMAGE_GROUP_SIZE
from app.models.image import Image
from app.parsers.errors import ImageFormatError, ImageGroupSizeError, ImageSizeError

EXTENSION_SHIFT = 6  # result of len("image/")


class ImageParser:
    def __init__(self) -> None:
        self.allowed_types = set(
            {
                'image/jpg',
                'image/jpeg',
                'image/png',
                'image/webp',
            }
        )

    async def parse_images(self, data_len: int, image_fds: List[UploadFile]):
        images = []

        if (data_len / len(image_fds)) > MAX_IMAGE_SIZE:
            raise ImageSizeError()
        if data_len > MAX_IMAGE_GROUP_SIZE:
            raise ImageGroupSizeError()

        for image_fd in image_fds:
            if image_fd.content_type not in self.allowed_types:
                raise ImageFormatError()

            extension = image_fd.content_type[EXTENSION_SHIFT:]
            image_name = f"{uuid.uuid4()}.{extension}"
            image_content = await image_fd.read()
            image = Image(name=image_name, content=image_content)
            images.append(image)

        return images
