from fastapi.exceptions import HTTPException
from fastapi.responses import Response
from fastapi import APIRouter, Header, UploadFile, status
from typing import List

from app.parsers.image_parser import ImageParser
from app.config.logger import setup_logger
from app.repositories.images import PersistentImageRepository
from app.schemas.image import ImageSchema
from app.utils.error import TicketAppError

logger = setup_logger(name=__name__)
router = APIRouter()


@router.post("/images/")
async def upload_images(
    files: List[UploadFile],
    content_length: int = Header(),
):

    try:
        images = await ImageParser().parse_images(content_length, files)
        images = PersistentImageRepository().add_images(images)
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )

    return list(map(lambda img: ImageSchema.from_model(img), images))


@router.get("/images/{name}")
async def get_image(name: str):

    try:
        image = PersistentImageRepository().get_image(name)
    except TicketAppError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error"
        )
    return Response(content=image.content, media_type=f"image/{image.extension}")
