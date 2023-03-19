from fastapi import status, APIRouter
from app.config.logger import setup_logger
from app.repositories.config import clear_db


logger = setup_logger(name=__name__)
router = APIRouter()


@router.post('/reset', status_code=status.HTTP_200_OK)
async def reset():
    logger.info("Clearing Database")
    clear_db()
    return "success"
