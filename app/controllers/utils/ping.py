from fastapi import status, APIRouter
from app.config.logger import setup_logger


logger = setup_logger(name=__name__)
router = APIRouter()


@router.get('/ping', status_code=status.HTTP_200_OK)
async def ping():
    logger.info("Ping endpoint")
    return "pong"
